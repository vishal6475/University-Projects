import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';
import EditRoundedIcon from '@material-ui/icons/EditRounded';
import DeleteIcon from '@material-ui/icons/Delete';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Modal from '@material-ui/core/Modal';
import Backdrop from '@material-ui/core/Backdrop';
import Fade from '@material-ui/core/Fade';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const ActionButtonsBox = styled.div`
display: flex;
flex-direction: row;
justify-content: space-around;
margin-bottom: 10px;
`;

const ShowActionButton = styled.button`
  border-radius: 5px;
  font-size: 18px;
  color: #3f51b5;
  border: none;
  cursor: pointer;
  background-color: transparent;

  &:hover {
    background-color: #9c9898;
  }
`;

const NoActionButton = styled.button`
  font-size: 18px;
  color: black;
  border: none;
  background-color: transparent;
`;

const TitleIconsBox = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 5px;
`;

const TitleBox = styled.div`
  max-width: 80%;
  overflow-wrap: break-word;
`;

const CountTimeBox = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const EditDeleteIconsBox = styled.div`
  display: flex;
  flex-direction: row;
`;

const EditIcon = styled(EditRoundedIcon)`
  background-color: transparent;
  border-radius: 20px;
  cursor: pointer;

  &:hover {
    background-color: #9c9898;
  }
`;

const DeleteQuizIcon = styled(DeleteIcon)`
  background-color: transparent;
  border-radius: 20px;
  cursor: pointer;

  &:hover {
    background-color: #9c9898;
  }
`;

const ModalBox = styled.div`
  display: flex;
  flex-direction: row;
  column-gap: 4px;
  justify-content: center;
`;

const ClickHere = styled.div`
  cursor: pointer;
  color: blue;
`;

const ConfirmYesNo = styled.div`
  cursor: pointer;
  color: blue;
  font-size: 18px;
`;

// classes for Material UI components- can't convert them to styled components as they use some internal Material UI styles
const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 345,
  },
  media: {
    height: 0,
    paddingTop: '56.25%',
    backgroundColor: '#bdbdbd'
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  },
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  paper: {
    backgroundColor: theme.palette.background.paper,
    border: '2px solid #000',
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

const QuizTile = ({ getAllQuizzes, title, thumbnail, quizID }) => {
  const history = useHistory();
  const classes = useStyles();

  // declaring use state variable for this page
  const [questionCount, setQuestionCount] = React.useState();
  const [totalTime, setTotalTime] = React.useState();
  const [gameQuizID, setGameQuizID] = React.useState();
  const [sessionID, setSessionID] = React.useState();
  const [isGameStarted, setGameStarted] = React.useState(0);
  const [quizIdToDelete, setQuizIdToDelete] = React.useState();

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  // use state variable and functions to show modal popup
  const [openModal, setModalOpen] = React.useState(false);
  const [showSessionIDModal, setShowSessionIDModal] = React.useState(0);
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = React.useState(0);

  const modalHandleOpen = () => {
    setModalOpen(true);
  };
  const modalHandleClose = () => {
    setModalOpen(false);
  };

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
    loadQuestionDetails(); // to load all the details on initial load
  }, []);

  // function to fetch all details of a quiz
  const loadQuestionDetails = async () => {
    const fetchQuizDetails = await fetch(`http://localhost:5005/admin/quiz/${quizID}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if the fetch call was successful or not
    if (fetchQuizDetails.status === 200) {
      const quizDetails = await fetchQuizDetails.json();

      if (quizDetails.active) { // checking if game is active or not and storing state
        setGameStarted(1);
      } else {
        setGameStarted(0);
      }

      setQuestionCount(quizDetails.questions.length);
      let totalTime = 0;
      quizDetails.questions.forEach(ques => (totalTime += ques.time));
      setTotalTime(totalTime);
    }
  }

  // to load quiz edit page
  const loadQuizEditPage = (quizID) => {
    history.push(`/quiz${quizID}`);
  }

  // to delete a quiz on confirmation
  const deleteQuiz = async (quizID) => {
    const fetchDeleteQuiz = await fetch(`http://localhost:5005/admin/quiz/${quizID}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    modalHandleClose();
    if (fetchDeleteQuiz.status === 200) {
      showAlertMessage('success', 'Quiz deleted successfully.');
      getAllQuizzes();
    } else {
      // const errorResponse = await fetchDeleteQuiz.json();
      showAlertMessage('error', 'Quiz deletion failed.');
    }
  }

  // function to copy session id to clipboard
  const copySessionID = () => {
    navigator.clipboard.writeText(`http://localhost:3000/player/join/${sessionID}`); // copied this line from net to copy link to clipboard
    showAlertMessage('success', 'Link copied to clipboard.');
    modalHandleClose();
  }

  // get session id of the quiz
  const getSessionId = async (quizID) => {
    const fetchSessionId = await fetch(`http://localhost:5005/admin/quiz/${quizID}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    if (fetchSessionId.status === 200) {
      const quizDetails = await fetchSessionId.json();
      setSessionID(quizDetails.active);
    }
  }

  // to start a quiz game on button click
  const startGame = async (e) => {
    const startQuiz = await fetch(`http://localhost:5005/admin/quiz/${e.target.value}/start`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if the fetch call was successful or not
    if (startQuiz.status === 200) {
      setGameStarted(1);
      setShowSessionIDModal(1); // to show modal for session ID
      setShowDeleteConfirmModal(0); // to NOT show modal for confirm delete quiz
      await getSessionId(e.target.value); // to fetch and store session ID and open modal box
      modalHandleOpen();
    } else {
      const errorResponse = await startQuiz.json();
      showAlertMessage('error', `Error in starting quiz. ${errorResponse.error}`);
    }
  }

  // function to advance game to next question
  const advanceGame = async (e) => {
    await getSessionId(e.target.value); // to fetch and store session ID
    const endQuiz = await fetch(`http://localhost:5005/admin/quiz/${e.target.value}/advance`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking what on what stage the quiz is and displaying pop up accordingly
    if (endQuiz.status === 200) {
      const response = await endQuiz.json();
      if (response.stage === questionCount) {
        setGameStarted(0);
        setGameQuizID(e.target.value);
        setShowSessionIDModal(0); // to show modal for results page
        setShowDeleteConfirmModal(0); // to NOT show modal for confirm delete quiz
        modalHandleOpen();
      } else {
        showAlertMessage('info', `This quiz has successfully advanced to question ${response.stage + 1} now.`);
      }
    } else {
      showAlertMessage('error', 'Unable to advance game to next question');
    }
  }

  // function to end an active game
  const endGame = async (e) => {
    await getSessionId(e.target.value); // to fetch and store session ID
    const endQuiz = await fetch(`http://localhost:5005/admin/quiz/${e.target.value}/end`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if the fetch call was successful or not
    if (endQuiz.status === 200) {
      setGameStarted(0);
      setGameQuizID(e.target.value);
      setShowSessionIDModal(0); // to show modal for results page
      setShowDeleteConfirmModal(0); // to NOT show modal for confirm delete quiz
      modalHandleOpen();
    } else {
      showAlertMessage('error', 'Unable to stop game due to technial issues.');
    }
  }

  // to transfer to results page
  const loadResultsPage = () => {
    history.push(`/game/results/${gameQuizID}/${sessionID}`);
  }

  return (
    <Card className={classes.root}>
      <TitleIconsBox>
        <TitleBox>
          {title}
        </TitleBox>
        <EditDeleteIconsBox>
          <div value={quizID} id={quizID} onClick={ (e) => loadQuizEditPage(e.currentTarget.id) } >
            <EditIcon value={quizID} />
          </div>
          <div value={quizID} id={quizID} onClick={ (e) => {
            setQuizIdToDelete(e.currentTarget.id);
            setShowDeleteConfirmModal(1);
            modalHandleOpen();
          }}>
            <DeleteQuizIcon value={quizID} />
          </div>
        </EditDeleteIconsBox>
      </TitleIconsBox>
      <CardMedia
        className={classes.media}
        image={`${thumbnail}`}
        title='thumbnail for quiz'
        alt='thumbnail for quiz'
      />
      <CardContent>
        <CountTimeBox>
          <div>Questions: {questionCount}</div>
          <div>Total time: {totalTime}s</div>
        </CountTimeBox>
      </CardContent>

      {/* to show the appropriate start, advance and end buttons depending on quiz active status */}
      <ActionButtonsBox >
        { isGameStarted === 0 &&
          <div>
            <ShowActionButton value={quizID} onClick={startGame} >Start</ShowActionButton>
          </div>
        }
        { isGameStarted === 1 &&
          <div>
            <NoActionButton>Start</NoActionButton>
          </div>
        }
        { isGameStarted === 1 &&
          <div>
            <ShowActionButton value={quizID} onClick={advanceGame} >Advance</ShowActionButton>
          </div>
        }
        { isGameStarted === 0 &&
          <div>
            <NoActionButton>Advance</NoActionButton>
          </div>
        }
        { isGameStarted === 1 &&
          <div>
            <ShowActionButton value={quizID} onClick={endGame} >Stop</ShowActionButton>
          </div>
        }
        { isGameStarted === 0 &&
          <div>
            <NoActionButton>Stop</NoActionButton>
          </div>
        }
      </ActionButtonsBox>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>

      {/* to display confirm modal box for delete quiz */}
      <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        className={classes.modal}
        open={openModal}
        onClose={modalHandleClose}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
      >
        <Fade in={openModal}>
          <div>{/* showing different details for different tasks */}
            { showSessionIDModal === 1 && showDeleteConfirmModal === 0 &&
            <div className={classes.paper}>
              <h2 id="show-session-id-modal">Game started. Session ID is {sessionID}.</h2>
              <ModalBox>
                <ClickHere onClick={copySessionID}>Click here</ClickHere>
                <div>to copy the link with session ID.</div>
              </ModalBox>
            </div>
            }
            { showSessionIDModal === 0 && showDeleteConfirmModal === 0 &&
            <div className={classes.paper}>
              <h2 id="show-results-page-modal">All questions completed and game has ended.</h2>
              <ModalBox>
                <ClickHere onClick={loadResultsPage}>Click here</ClickHere>
                <div>to show the results page.</div>
              </ModalBox>
            </div>
            }
            { showDeleteConfirmModal === 1 &&
            <div className={classes.paper}>
              <h2 id="confirm-quiz-delete-modal">Confirm to delete quiz.</h2>
              <ModalBox>
                <ConfirmYesNo onClick={() => { deleteQuiz(quizIdToDelete); }}>Yes</ConfirmYesNo>
                <div>/</div>
                <ConfirmYesNo onClick={modalHandleClose}>No</ConfirmYesNo>
              </ModalBox>
            </div>
            }
          </div>
        </Fade>
      </Modal>
    </Card>
  );
}

QuizTile.propTypes = {
  getAllQuizzes: PropTypes.func,
  title: PropTypes.string,
  thumbnail: PropTypes.string,
  quizID: PropTypes.number,
  questionCount: PropTypes.number,
  totalTime: PropTypes.number
}

export default QuizTile;
