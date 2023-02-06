import React from 'react';
import ResultsBarChart from '../components/ResultsBarChart';
import { StoreContext } from '../utils/store';
import { useParams, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const MainBox = styled.div`
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

const TableHeader = styled(TableCell)`
  background-color: black;
`;

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// Main Game Results function
const GameResults = () => {
  const params = useParams();
  const history = useHistory();

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  // declaring use state variable for this page
  const [topUsersStats, setTopUsersStats] = React.useState();
  const [correctQuestionsStats, setCorrectQuestionsStats] = React.useState();
  const [responseTimeStats, setResponseTimeStats] = React.useState();

  // checking if the user is authorized to see this page
  if (!localStorage.getItem('token')) {
    history.push('/login');
  }

  React.useEffect(() => {
    // setting the logout and page location to display the components correctly
    if (showLogout === 0) {
      setShowLogout(1);
    }
    if (pagelocation !== 4) {
      setPageLocation(4);
    }
    getGameResults(); // to load all the game results on initial page load
  }, []);

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

  // function to calculate various stats for the results
  const getGameResults = async () => {
    // calling fetch to get the results
    const fetchGameResults = await fetch(`http://localhost:5005/admin/session/${params.sid}/results`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // calling fetch to get this quiz details as well to access the question points
    const fetchQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if both fetch calls were successful or not
    if (fetchGameResults.status === 200 && fetchQuiz.status === 200) {
      // storing the details required
      const gameResults = await fetchGameResults.json();
      const quiz = await fetchQuiz.json();
      const quizPoints = [];
      quiz.questions.forEach(question => quizPoints.push(question.points)); // to store points for each question
      const noOfPlayers = gameResults.results.length;
      const noOfQuestions = quiz.questions.length;

      // to get table of top users
      const topUsersData = [];

      // to get stats of correct questions
      const allCorrectQuestionsPoints = [];
      for (let i = 1; i <= noOfQuestions; i++) {
        const barChartValue = { text: `Q${i}`, value: 0 };
        allCorrectQuestionsPoints.push(barChartValue);
      }

      // to get stats of average response times
      const averageResponseData = [];
      for (let i = 1; i <= noOfQuestions; i++) {
        const barChartValue = { text: `Q${i}`, answeredTimes: 0, value: 0 };
        averageResponseData.push(barChartValue);
      }

      // checking each result of the fetched response to calculate details for all players
      gameResults.results.forEach((result) => {
        // to calculate stats for top users
        const playerStats = { name: '', correctResponses: 0, totalPoints: 0 };
        result.answers.forEach((answer, index) => {
          if (answer.correct) {
            playerStats.totalPoints += quizPoints[index];
            playerStats.correctResponses += 1;
          }
        })
        playerStats.name = result.name;
        topUsersData.push(playerStats);

        // to calculate stats for correct responses and average responses times
        for (let i = 0; i < noOfQuestions && i < result.answers.length; i++) {
          allCorrectQuestionsPoints[i].value += result.answers[i].correct ? 1 : 0; // for correct responses
          if (result.answers[i].questionStartedAt && result.answers[i].answeredAt) { // for average response time
            averageResponseData[i].answeredTimes += 1;
            const startTime = new Date(result.answers[i].questionStartedAt);
            const endTime = new Date(result.answers[i].answeredAt);
            const timeTaken = endTime - startTime;
            averageResponseData[i].value += (timeTaken / 1000);
          }
        }
      });
      sortTopUsersData(topUsersData); // to sort top users data and show for only top 5 users

      // calculating percentage now
      for (let i = 0; i < quiz.questions.length; i++) {
        allCorrectQuestionsPoints[i].value = (allCorrectQuestionsPoints[i].value * 100) / noOfPlayers;
      }
      setCorrectQuestionsStats(allCorrectQuestionsPoints);

      // to get stats for response times
      const chartAverageResponseData = [];
      for (let i = 0; i < noOfQuestions; i++) {
        const barChartValue = { text: `Q${i + 1}`, value: 0 };
        if (averageResponseData[i].value > 0) {
          barChartValue.value = averageResponseData[i].value / averageResponseData[i].answeredTimes;
        }
        chartAverageResponseData.push(barChartValue);
      }
      setResponseTimeStats(chartAverageResponseData);

      // move to top of page
      window.scrollTo(0, 0);
    } else { // to show any error messages in case of failure
      showAlertMessage('error', 'Unable to fetch game results.');
    }
  }

  // fuction to sort top users data and show for only top 5 users
  const sortTopUsersData = (topUsersData) => {
    const noOfPlayers = topUsersData.length;

    // sort based on total points (value)
    for (let i = 0; i < noOfPlayers - 1; i++) {
      for (let j = noOfPlayers - 2; j >= i; j--) {
        if (topUsersData[j].totalPoints < topUsersData[j + 1].totalPoints) {
          const tempData = topUsersData[j];
          topUsersData[j] = topUsersData[j + 1];
          topUsersData[j + 1] = tempData;
        }
      }
    }

    // storing data for top 5 users
    const finalTableData = [];
    for (let i = 0; i < noOfPlayers && i < 5; i++) {
      finalTableData.push(topUsersData[i]);
    }
    setTopUsersStats(finalTableData);
  }

  // return function for all the components on this page
  return (
    <MainBox>
      <HeadingBox>
        Table of top users (max 5 shown):
      </HeadingBox>
      <div> {/* producing table for top users stats */}
        <TableContainer component={Paper}>
          <Table aria-label="table-for-top-user-stats">
            <TableHead>
              <TableRow>
                {/* for some reason, white color doesn't gets applied through styled component, so had to put it here */}
                <TableHeader style={{ color: 'white' }}>Player Name</TableHeader>
                <TableHeader align="right" style={{ color: 'white' }}>Correct Responses</TableHeader>
                <TableHeader align="right" style={{ color: 'white' }}>Total Points</TableHeader>
              </TableRow>
            </TableHead>
            <TableBody>
              {topUsersStats && topUsersStats.map((stats, index) => (
                <TableRow key={index}>
                  <TableCell component="th" scope="row">
                    {stats.name}
                  </TableCell>
                  <TableCell align="right">{stats.correctResponses}</TableCell>
                  <TableCell align="right">{stats.totalPoints}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </div>

      <HeadingBox>
        Percentage of correct responses for each question:
      </HeadingBox>
      <div> {/* calling ResultsBarChart component to produce the bar chart for correct responses */}
        { correctQuestionsStats &&
          <ResultsBarChart data={correctQuestionsStats} />
        }
      </div>

      <HeadingBox>
        Average response time per question (in seconds):
      </HeadingBox>
      <div> {/* calling ResultsBarChart component to produce the bar chart for average responses */}
        { responseTimeStats &&
          <ResultsBarChart data={responseTimeStats}/>
        }
      </div>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </MainBox>
  );
}

export default GameResults;
