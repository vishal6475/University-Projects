import React from 'react';
import QuizTile from '../components/QuizTile';
import { useHistory } from 'react-router-dom';
import { NewGameImage } from '../images/NewGameImage.json';
import styled from 'styled-components';
import Container from '@material-ui/core/Container';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import { StoreContext } from '../utils/store';

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const CreateNewGameBox = styled.div`
  padding-top: 50px;
  max-width: 345;
`;

const GameTextfield = styled(TextField)`
  z-index: 0;
`;

const AllQuizzesBox = styled.div`
  display: grid;
  margin-top: 30px;
  grid-template-columns: 5fr 5fr 5fr;
  row-gap: 30px;
  column-gap: 20px;

  @media (max-width: 960px) {
    grid-template-columns: 5fr 5fr; 
  }

  @media (max-width: 650px) {
    grid-template-columns: 5fr;
    padding: 0;
    margin-left: calc(50vw - 30px - 172.5px);
  }
  
  @media (max-width: 650px) {
    grid-template-columns: 5fr;
    align-content: center;
  }
`;

// Main Dashboard function
function Dashboard () {
  const history = useHistory();

  // use state variables for this dashboard page
  const [newGameName, setNewGameName] = React.useState('');
  const [allQuizzesTiles, setAllQuizzesTiles] = React.useState([]);

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  // check for authorized user and redirect
  if (!localStorage.getItem('token')) {
    history.push('/login');
  }

  React.useEffect(() => {
    window.scrollTo(0, 0); // scroll to top of window
    getAllQuizzes(); // to display and load all the details in initial load

    // setting the logout and page location to display the components correctly
    if (showLogout === 0) {
      setShowLogout(1);
    }
    if (pagelocation !== 1) {
      setPageLocation(1);
    }
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

  // method to fetch all quiz details for the admin and load them
  const getAllQuizzes = async () => {
    const fetchAllQuizzes = await fetch('http://localhost:5005/admin/quiz/', {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if fetch was successful or failed
    if (fetchAllQuizzes.status === 200) {
      const allQuizzes = await fetchAllQuizzes.json();
      // adding component QuizTile for each quiz and displaying in a card
      setAllQuizzesTiles(allQuizzes.quizzes.map((quiz, index) =>
      <QuizTile key={index} getAllQuizzes={getAllQuizzes} title={quiz.name} thumbnail={quiz.thumbnail} quizID={quiz.id} />
      ));
    }
  }

  // method to verify name and create a new game
  const createGame = async () => {
    if (newGameName.length === 0) {
      showAlertMessage('warning', 'Please enter a name to create new game.');
    } else if (newGameName.length > 60) {
      showAlertMessage('warning', 'Please enter a name shorter than 61 characters.');
    } else {
      const newGameDetails = {
        name: newGameName,
        thumbnail: NewGameImage
      };

      // calling fetch to create a new game
      const fetchNewGame = await fetch('http://localhost:5005/admin/quiz/new', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(newGameDetails),
      })

      // if game creation is successful, proceed further
      if (fetchNewGame.status === 200) {
        showAlertMessage('success', 'New game created successfully.');
        const response = await fetchNewGame.json();

        const updatedNewGameDetails = {
          name: newGameName,
          thumbnail: NewGameImage
        };

        // now fetch all quizzes for the admin again and display them
        await fetch(`http://localhost:5005/admin/quiz/${response.quizId}`, {
          method: 'PUT',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(updatedNewGameDetails),
        })
        getAllQuizzes(); // to load all the quizzes
        setNewGameName('');
      } else { // to show any error messages in case of failure
        showAlertMessage('error', 'New game creation failed. Please try again.');
      }
    }
  }

  // for displaying dashboard components
  return (
    <>
    <Container fixed>
      <AllQuizzesBox>
        <CreateNewGameBox>
          <GameTextfield
            variant="outlined"
            margin="normal"
            fullWidth
            label="Enter Game Name*"
            helperText="Maximum character limit: 60"
            value={newGameName}
            onChange={(e) => setNewGameName(e.target.value)}
            multiline
            rowsMax={3}
          />
          <Button fullWidth variant='contained' color='primary' onClick={createGame}>Create Game</Button>
        </CreateNewGameBox>
        {allQuizzesTiles}
      </AllQuizzesBox>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Container>
    </>
  );
}

export default Dashboard;
