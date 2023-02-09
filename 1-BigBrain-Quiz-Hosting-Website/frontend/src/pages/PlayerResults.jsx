import React from 'react';
import { StoreContext } from '../utils/store';
import QuestionResults from '../components/QuestionResults';
import styled from 'styled-components';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const ContainerBox = styled.div`
  width: 80vw;
  margin: auto;
  margin-top: 20px;
`;

const HeadingBox = styled.div`
  background-color: #8b8c8b;
  padding: 5px 10px;
  margin-top: 30px;
  margin-bottom: 10px;
`;

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

function PlayerResults () {
  // declaring use state variable for this page
  const playerID = localStorage.getItem('playerID');
  const [allQuestionStats, setQuestionStats] = React.useState([]);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  // functions to show alert messages
  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  };

  const showAlertMessage = (alertType, alertMessage) => {
    setOpen(false);
    setAlertMessage(alertMessage);
    setAlertSeverity(alertType);
    setOpen(true);
  }

  React.useEffect(() => {
    // setting the logout and page location to display the components correctly
    if (showLogout === 1) {
      setShowLogout(0);
    }
    getResults(); // load the results on initial load
  }, []);

  // function to fetch results
  const getResults = async () => {
    const fetchPlayerResults = await fetch(`http://localhost:5005/play/${playerID}/results`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })

    // checking if the fetch call was successful or not
    if (fetchPlayerResults.status === 200) {
      const playerResults = await fetchPlayerResults.json();
      setQuestionStats(playerResults);
    } else { // to show any error messages in case of failure
      const errorResponse = await fetchPlayerResults.json();
      showAlertMessage('error', `Unable to fetch player results. ${errorResponse.error}.`);
    }
  }

  // calculate time taken
  const getTimeTaken = (startDate, endDate) => {
    const startTime = new Date(startDate);
    const currentTime = new Date(endDate);
    const timeLapsed = (currentTime - startTime) / 1000;
    return timeLapsed;
  }

  // function to show date in desired format
  const convertToDate = (rawDate) => {
    if (!rawDate) {
      return 'Not applicable';
    } else {
      const getDate = new Date(rawDate);
      return `${months[getDate.getMonth()]} ${getDate.getDate()} ${getDate.getFullYear()} ${getDate.getHours()}:${getDate.getMinutes()}:${getDate.getSeconds()}`;
    }
  }

  return (
    <ContainerBox>
      <HeadingBox>
        Results:
      </HeadingBox>
      {/* to show stats for all the questions */}
      {allQuestionStats.map((stats, index) => {
        return <QuestionResults
        key={index}
        questionNumber={index + 1}
        time={getTimeTaken(stats.questionStartedAt, stats.answeredAt)}
        start={convertToDate(stats.questionStartedAt)}
        answered={convertToDate(stats.answeredAt)}
        type={stats.answerIds.length === 1 ? 'S' : 'M'}
        response={stats.correct}
        />
      })
      }

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={10000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </ContainerBox>
  );
}

export default PlayerResults;
