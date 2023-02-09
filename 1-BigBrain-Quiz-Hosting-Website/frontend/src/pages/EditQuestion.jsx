import React from 'react';
import QuizDetails from '../components/QuizDetails';
import { StoreContext } from '../utils/store';
import { useParams, useHistory } from 'react-router-dom';
import Container from '@material-ui/core/Container';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import styled from 'styled-components';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const UpdateQuestionBox = styled.div`
  background-color: #8b8c8b;
  padding: 5px 10px;
  margin-top: 20px;
`;

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// Main Edit Question function
const EditQuestion = () => {
  const params = useParams();
  const history = useHistory();

  // use state variables for this page
  const [questionDetails, setQuestionDetails] = React.useState();

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

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

  // checking if the user is authorized to see this page
  if (!localStorage.getItem('token')) {
    history.push('/login');
  }

  React.useEffect(() => {
    // scroll to top of window
    window.scrollTo(0, 0);

    // setting the logout and page location to display the components correctly
    if (showLogout === 0) {
      setShowLogout(1);
    }
    if (pagelocation !== 3) {
      setPageLocation(3);
    }
    localStorage.setItem('quiz_id', params.qid);
    getQuestion(); // to get all details of question on initial page load
  }, []);

  // function calling fetch to get all question details
  const getQuestion = async () => {
    const fetchQuizDetails = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    // checking if the fetch call was successful or not
    if (fetchQuizDetails.status === 200) {
      const quizDetails = await fetchQuizDetails.json();
      const qData = quizDetails.questions[params.qsid - 1];

      // calling component QuizDetails to show details of the question
      setQuestionDetails(() => {
        return <QuizDetails
        qtext={qData.question}
        qtype={qData.type}
        qpoints={qData.points}
        qtime={qData.time}
        qNoOfAnswers={qData.answers.length}
        qAnswers={qData.answers}
        qYoutubeURL={qData.youtubeURL}
        qImageSRC={qData.imageSRC}
        qImageName={qData.imageName}
        />
      });
    } else { // to show any error messages in case of failure
      const errorResponse = await fetchQuizDetails.json();
      showAlertMessage('error', `Unable to get question details. ${errorResponse.error}.`);
    }
  }

  // returing all the components to show edit question details
  return (
    <Container fixed>
      <UpdateQuestionBox>
        Update question details:
      </UpdateQuestionBox>

      <div>
        {questionDetails}
      </div>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default EditQuestion;
