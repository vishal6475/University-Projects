import React from 'react';
import QuizQuestions from '../components/QuizQuestions';
import QuizDetails from '../components/QuizDetails';
import { fileToDataUrl } from '../components/helpers.js';
import { useParams, useHistory } from 'react-router-dom';
import { StoreContext } from '../utils/store';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import styled from 'styled-components';
import Modal from '@material-ui/core/Modal';
import Backdrop from '@material-ui/core/Backdrop';
import Fade from '@material-ui/core/Fade';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const ContainerBox = styled.div`
  width: 80vw;
  margin: auto;
  margin-top: 20px;
`;

const HeadingBox = styled.div`
  background-color: #8b8c8b;
  padding: 5px 10px;
  margin-top: 20px;
`;

const UpdateThumbnailBox = styled.div`
  margin-top: 5px;
`;

const StyledCard = styled(Card)`
  max-width: 600;
`;

const SaveButtonBox = styled.div`
  display: flex;
  justify-content: center;
`;

const SaveButton = styled(Button)`
  margin-top: 10px;
`;

const QuizTitleBox = styled.div`
  margin-top: 30px;
`;

const QuizNameTextfield = styled(TextField)`
  width: 100%;
  z-index: 0;
`;

const QuizGridBox = styled.div`
  margin-top: 10px;
  display: grid;
  grid-template-columns: 2.5fr 5fr;
  column-gap: 10px;

  @media (max-width: 700px) {
    grid-template-columns: 5fr;
  }
`;

const QuizDetailsBox = styled.div`
  padding: 0 20px;
`;

const ModalBox = styled.div`
  display: flex;
  flex-direction: row;
  column-gap: 4px;
  justify-content: center;
`;

const ConfirmYesNo = styled.div`
  cursor: pointer;
  color: blue;
  font-size: 18px;
`;

// classes for Material UI components- can't convert them to styled components as they use some internal Material UI styles
const useStyles = makeStyles((theme) => ({
  media: {
    height: 0,
    paddingTop: '56.25%',
    backgroundColor: '#bdbdbd'
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

// Main EditQuiz page function
const EditQuiz = () => {
  const params = useParams();
  const history = useHistory();
  const classes = useStyles();

  // declaring use state variable for this page
  const [fullQuizDetails, setFullQuizDetails] = React.useState();
  const [quizTitle, setQuizTitle] = React.useState('');
  const [allQuestions, setAllQuestions] = React.useState([]);
  const [currentThumbnail, setCurrentThumbnail] = React.useState([]);
  const [thumbnail, setThumbnail] = React.useState();
  const [questionIdToDelete, setQuestionIdToDelete] = React.useState();

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

  // use state variable to show modal popup
  const [openModal, setModalOpen] = React.useState(false);

  // functions to show modal popup
  const modalHandleOpen = (value) => {
    setModalOpen(true);
    setQuestionIdToDelete(value);
  };
  const modalHandleClose = () => {
    setModalOpen(false);
  };

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
    if (pagelocation !== 2) {
      setPageLocation(2);
    }

    // function to load all details on initial page load
    getQuiz();
  }, []);

  // function calling fetch to load all details on initial page load
  const getQuiz = async () => {
    const fetchQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      }
    })

    // checking if fetch was successful or not
    if (fetchQuiz.status === 200) {
      const quiz = await fetchQuiz.json();
      setCurrentThumbnail(quiz.thumbnail);
      setFullQuizDetails(quiz);
      setAllQuestions(quiz.questions);
      setQuizTitle(quiz.name);
    }
  }

  // function to convert upload image and validate the format
  const getQuizThumbnail = async (file) => {
    if (file) {
      const imageSrc = await fileToDataUrl(file);
      if (imageSrc === 'Error') {
        showAlertMessage('warning', 'Please upload only png or jpeg images.');
        document.getElementById('quiz-thumbnail-picture').value = null;
      } else {
        setThumbnail(file);
      }
    }
  }

  // function to validate all input details and save them
  const saveQuizDetails = async () => {
    let imageSrc = '';
    if (thumbnail) {
      imageSrc = await fileToDataUrl(thumbnail);
    }
    if (quizTitle.length === 0) {
      showAlertMessage('warning', 'Please enter a quiz name.');
    } else if (quizTitle.length > 60) {
      showAlertMessage('warning', 'Please enter a name shorter than 61 characters.');
    } else if (imageSrc === 'Error' && thumbnail) {
      showAlertMessage('warning', 'Please upload only png or jpeg images.');
    } else {
      // fetching all details for the quiz first which will be updated and sent back to server
      const fetchQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        }
      })

      // checking status of fetch
      if (fetchQuiz.status === 200) {
        const quiz = await fetchQuiz.json();
        quiz.name = quizTitle;
        if (thumbnail) {
          quiz.thumbnail = imageSrc;
        }

        // finally sending back the updated details to server
        const updateQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
          method: 'PUT',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(quiz),
        })

        // checking status of update details
        if (updateQuiz.status === 200) {
          setCurrentThumbnail(quiz.thumbnail);
          showAlertMessage('success', 'Quiz details have been updated successfully.');
        } else { // to show any error messages in case of failure
          showAlertMessage('error', 'Error in updating quiz details.');
        }
      } else { // to show any error messages in case of failure
        showAlertMessage('error', 'Error in updating quiz details.');
      }
    }
  }

  // to trasfer to edit question page on button click
  const editQuestion = async (questionId) => {
    history.push(`/quiz${params.qid}/question${questionId}`);
  }

  // function to delete a question
  const deleteQuestion = async (questionId) => {
    const quiz = fullQuizDetails;
    quiz.questions.splice(questionId - 1, 1);

    // calling fetch to delete question
    const fetchDeleteQuestion = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(quiz),
    })
    modalHandleClose();

    // checking if the fetch call was successful or not
    if (fetchDeleteQuestion.status === 200) {
      showAlertMessage('success', 'Question deleted successfully.');
      getQuiz();
    } else { // to show any error messages in case of failure
      const errorResponse = fetchDeleteQuestion.json();
      showAlertMessage('error', `Error in deleting question. ${errorResponse.error}`);
    }
  }

  return (
    <ContainerBox>
      <HeadingBox>
        Update quiz details:
      </HeadingBox>
      <QuizGridBox>
        <div>
          <div>
            <StyledCard>
              <CardMedia
                className={classes.media}
                image={`${currentThumbnail}`}
                title={quizTitle}
                alt='thumbnail for quiz'
              />
            </StyledCard>
          </div>
          <UpdateThumbnailBox>
            <div>
              Update thumbnail:
            </div>
            <div>
              <input type="file" id='quiz-thumbnail-picture' onChange={e => { getQuizThumbnail(e.target.files[0]) }} />
            </div>
          </UpdateThumbnailBox>
        </div>
        <QuizTitleBox>
          <QuizNameTextfield
            label='Quiz name*'
            value={quizTitle}
            onChange={e => setQuizTitle(e.target.value)}
            variant='outlined'
            helperText="Maximum character limit: 60"
            multiline
            rowsMax={3}
          />
        </QuizTitleBox>
      </QuizGridBox>

      <SaveButtonBox>
        <SaveButton variant="contained" color="primary" onClick={ saveQuizDetails }>
          Save changes
        </SaveButton>
      </SaveButtonBox>
      { allQuestions.length > 0 &&
      <HeadingBox>
        Update quiz questions:
      </HeadingBox>
      }

      {/* to show all the questions details */}
      {allQuestions.map((question, index) => {
        return <QuizQuestions
          key={index}
          index={index + 1}
          editQuestion={editQuestion}
          openModalBox={modalHandleOpen}
          question={question.question}
          points={question.points}
          time={question.time}
          type={question.type}
          answers={question.answers.length}
          youtubeURL={question.youtubeURL}
          imageName={question.imageName}
        />
      })
      }

      <HeadingBox>
        Add new question:
      </HeadingBox>
      <QuizDetailsBox>
        <QuizDetails getQuiz={getQuiz} />
      </QuizDetailsBox>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>

      {/* to display confirm modal box for delete question */}
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
          <div className={classes.paper}>
            <h2 id="confirm-question-delete-modal">Confirm to delete question.</h2>
            <ModalBox>
              <ConfirmYesNo onClick={() => { deleteQuestion(questionIdToDelete); }}>Yes</ConfirmYesNo>
              <div>/</div>
              <ConfirmYesNo onClick={modalHandleClose}>No</ConfirmYesNo>
            </ModalBox>
          </div>
        </Fade>
      </Modal>
    </ContainerBox>
  );
}

export default EditQuiz;
