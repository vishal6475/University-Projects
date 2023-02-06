import React from 'react';
import styled from 'styled-components';
import QuizAnswers from '../components/QuizAnswers';
import { useParams } from 'react-router-dom';
import { StoreContext } from '../utils/store';
import { fileToDataUrl } from '../components/helpers.js';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import { makeStyles } from '@material-ui/core/styles';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import PropTypes from 'prop-types';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const NewQuestionBox = styled.div`
  display: grid;
  grid-template-columns: 5fr 5fr;
  row-gap: 30px;

  @media (max-width: 650px) {
    display: flex;
    flex-direction: column;
  }
`;

const QuestionBox = styled.div`
  margin-bottom: 30px;
  margin-top: 10px;
`;

const QuestionTextfield = styled(TextField)`
  width: 100%;
`

const AttachURLTextfield = styled(TextField)`
  width: 200px;
`

const UploadImageBox = styled.div`
  color: #7d7d7a;
`;

const OuterAnswersBox = styled.div`
  border-style: solid;
  border-radius: 10px;
  border-width: 1px;
  padding: 20px;
  margin-top: 10px;
`;

const InnerAnswersBox = styled.div`
  display: grid;
  grid-template-columns: 5fr 5fr;
  row-gap: 30px;
`;

const AttachOneMessageBox = styled.div`
  color: grey;
  width: 220px;
  font-size: 0.75rem;
  font-weight: bold;
`;

const AddUpdateButtonBox = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 20px;
`;

// classes for Material UI components- can't convert them to styled components as they use some internal Material UI styles
const useStyles = makeStyles((theme) => ({
  formControl: {
    margin: theme.spacing(0),
    minWidth: 200,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
}));

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// Main Quiz details function
function QuizDetails ({ getQuiz, qtext, qtype, qpoints, qtime, qNoOfAnswers, qAnswers, qYoutubeURL, qImageSRC, qImageName }) {
  const classes = useStyles();
  const params = useParams();

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

  // declaring use state variable for this page
  const [question, setQuestion] = React.useState('');
  const [questionType, setQuestionType] = React.useState('S');
  const [points, setPoints] = React.useState('');
  const [time, setTime] = React.useState('');
  const [noOfAnswers, setNoOfAnswers] = React.useState(2);
  const [singleAnswerValue, setSingleAnswerValue] = React.useState();
  const [multipleAnswerValues, setMultipleAnswerValues] = React.useState([]);
  const [answerTexts, setAnswerTexts] = React.useState(['', '', '', '', '', '']);
  const [youtubeURL, setYoutubeURL] = React.useState('');
  const [answerPhoto, setAnswerPhoto] = React.useState('');
  const [answerPhotoName, setAnswerPhotoName] = React.useState('');

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

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
    if (showLogout === 0) {
      setShowLogout(1);
    }
    setPageLocation(pagelocation);

    // to load the question details when coming from edit question page
    if (qtype) {
      setQuestion(qtext);
      setQuestionType(qtype);
      setPoints(qpoints);
      setTime(qtime);
      setNoOfAnswers(qNoOfAnswers);
      const tempAnswers = answerTexts;
      for (let i = 0; i < qAnswers.length; i++) {
        tempAnswers[i] = qAnswers[i];
      }
      setAnswerTexts(tempAnswers);
      setYoutubeURL(qYoutubeURL);
      setAnswerPhoto(qImageSRC);
      setAnswerPhotoName(qImageName);
    }
  }, []);

  // function to update the selected question type
  const selectQuestionType = (value) => {
    setQuestionType(value);
    if (value === 'S') {
      setMultipleAnswerValues([]);
    } else if (value === 'M') {
      setSingleAnswerValue();
    }
  }

  // function to update the list of selected multiple values for an answer
  const updateMultipleAnswerValues = (e) => {
    let tempMultipleValues = [];
    if (e.target.checked) {
      tempMultipleValues = multipleAnswerValues.concat(parseInt(e.target.value));
      tempMultipleValues.sort(function (a, b) { return a - b }); // taken this line from w3schools to sort based on numbers
      setMultipleAnswerValues(tempMultipleValues);
    } else {
      multipleAnswerValues.forEach(value => {
        if (value !== parseInt(e.target.value)) {
          tempMultipleValues.push(value);
        }
      })
      tempMultipleValues.sort(function (a, b) { return a - b });
      setMultipleAnswerValues(tempMultipleValues);
    }
  }

  // function to update the each answer text
  const updateAnswers = (index, value) => {
    const newAnswers = [...answerTexts];
    newAnswers[index] = value;
    setAnswerTexts(newAnswers);
  }

  // function to reset details on successful operation
  const resetQuestionDetails = () => {
    setQuestion('');
    setQuestionType('S');
    setPoints('');
    setTime('');
    setNoOfAnswers(2);
    setSingleAnswerValue();
    setMultipleAnswerValues([]);
    setAnswerTexts(['', '', '', '', '', '']);
    setYoutubeURL('');
    setAnswerPhoto('');
    setAnswerPhotoName('');
    document.getElementById('answer-image-input').value = null;
  }

  // function to set the answer image src and name
  const setAnswerImage = async (file) => {
    if (file) {
      const imageSrc = await fileToDataUrl(file);
      if (imageSrc === 'Error') {
        removeAnswerImage();
        showAlertMessage('warning', 'Please upload only png or jpeg images.');
      } else {
        setAnswerPhoto(imageSrc);
        setAnswerPhotoName(file.name);
      }
    } else {
      setAnswerPhoto('');
      setAnswerPhotoName('');
    }
  }

  // function to set the youtube URL
  const updateYoutubeURL = (value) => {
    setYoutubeURL(value);
  }

  // function to remove answer on remove button click
  const removeAnswerImage = () => {
    if (answerPhotoName.length === 0) {
      showAlertMessage('info', 'There is no image to remove.');
    } else {
      showAlertMessage('info', 'Image removed successfully.');
    }
    setAnswerPhoto('');
    setAnswerPhotoName('');
    document.getElementById('answer-image-input').value = null;
  }

  // function to verify all details and add/update a question details
  const addQuestion = async () => {
    // validating all input fields
    if (question.length === 0) {
      showAlertMessage('warning', 'Please enter question text.');
    } else if (points.length === 0) {
      showAlertMessage('warning', 'Please enter points.');
    } else if (isNaN(points)) {
      showAlertMessage('warning', 'Please enter only numbers in points.');
    } else if (points > 9999) {
      showAlertMessage('warning', 'Please enter points less than or equal to 9999.');
    } else if (time.length === 0) {
      showAlertMessage('warning', 'Please select time.');
    } else if (youtubeURL.length > 0 && answerPhotoName.length > 0) {
      showAlertMessage('warning', 'Please attach only one of Youtube URL or an image.');
    } else if (answerPhotoName.length > 0 && answerPhoto === 'Error') {
      showAlertMessage('warning', 'Please upload only png or jpeg images.');
    } else if (questionType === 'S' && !singleAnswerValue) {
      showAlertMessage('warning', 'Please select a correct answer.');
    } else if (questionType === 'M' && multipleAnswerValues.length === 0) {
      showAlertMessage('warning', 'Please select correct answer(s) for this question.');
    } else {
      let isAnswersFilled = true;
      for (let i = 0; i < noOfAnswers; i++) {
        if (answerTexts[i].length === 0) {
          isAnswersFilled = false;
        }
      }

      if (isAnswersFilled === false) {
        showAlertMessage('warning', 'Please enter all the answers.');
      } else { // all validations passed, add/update question
        const action = pagelocation === 2 ? 'added' : 'updated';
        // first intial data to copy latest data over it
        const fetchQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
          method: 'GET',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          }
        })

        // storing the details entered for this question
        if (fetchQuiz.status === 200) {
          const quiz = await fetchQuiz.json();
          let correctAnswers = [];
          const answers = [];

          for (let i = 0; i < noOfAnswers; i++) {
            answers.push(answerTexts[i]);
          }
          if (questionType === 'S') {
            correctAnswers = [singleAnswerValue];
          } else {
            correctAnswers = multipleAnswerValues;
          }

          const questionBody = {
            question: question,
            type: questionType,
            points: parseInt(points),
            time: time,
            answers: answers,
            correctAnswers: correctAnswers,
            youtubeURL: youtubeURL,
            imageSRC: answerPhoto,
            imageName: answerPhotoName
          };

          // adding or updating question depending on page location
          if (pagelocation === 2) { // for adding question
            if (quiz.questions.length === 0) {
              quiz.questions = [questionBody];
            } else {
              quiz.questions.push(questionBody);
            }
          } else {
            quiz.questions[params.qsid - 1] = questionBody; // for updating question
          }

          const quizBody = {
            questions: quiz.questions,
            name: quiz.name,
            thumbnail: quiz.thumbnail
          };

          // finally sending the updated data to server
          const fetchUpdateQuiz = await fetch(`http://localhost:5005/admin/quiz/${params.qid}`, {
            method: 'PUT',
            headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify(quizBody),
          })

          if (fetchUpdateQuiz.status === 200) {
            // to show success message
            showAlertMessage('success', `Question ${action} successfully.`);

            if (pagelocation === 2) {
              // resetting all the fields
              resetQuestionDetails();
              getQuiz();
            }
          } else {
            const errorResponse = await fetchUpdateQuiz.json();
            // to show error message
            showAlertMessage('error', `Unable to ${action} question. ${errorResponse.error}.`);
          }
        } else {
          const errorResponse = await fetchQuiz.json();
          // to show error message
          showAlertMessage('error', `Unable to ${action} question. ${errorResponse.error}.`);
        }
      }
    }
  }

  return (
    <div>
      <div>
        <form>
            <QuestionBox>
              <QuestionTextfield
                label="Question*"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                multiline
                rowsMax={3}
              />
            </QuestionBox>
          <NewQuestionBox> {/* to show all the input elements for a question, allowing admin to select details */}
            <div>
              <FormControl className={classes.formControl}>
                <InputLabel id="question-type-select-label">Question Type*</InputLabel>
                <Select
                  labelId="question-type-select-label"
                  id="question-type-select"
                  value={questionType}
                  onChange={(e) => selectQuestionType(e.target.value)}
                >
                  <MenuItem value='S'>Single</MenuItem>
                  <MenuItem value='M'>Multiple</MenuItem>
                </Select>
              </FormControl>
            </div>

            <div>
              <TextField
                label="Points*"
                value={points}
                helperText='Only numbers (max: 9999)'
                onChange={(e) => setPoints(e.target.value)}
              />
            </div>

            <div> {/* showing all form elements to enter data */}
              <FormControl className={classes.formControl}>
                <InputLabel id="time-select-label">Time to Complete*</InputLabel>
                <Select
                  labelId="time-select-label"
                  id="time-select"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                >
                  <MenuItem value={5}>5 seconds</MenuItem>
                  <MenuItem value={10}>10 seconds</MenuItem>
                  <MenuItem value={15}>15 seconds</MenuItem>
                  <MenuItem value={30}>30 seconds</MenuItem>
                  <MenuItem value={60}>60 seconds</MenuItem>
                  <MenuItem value={90}>90 seconds</MenuItem>
                  <MenuItem value={120}>120 seconds</MenuItem>
                </Select>
              </FormControl>
            </div>

            <div>
              <FormControl className={classes.formControl}>
                <InputLabel id="number-of-answers-select-label">Number of Answers*</InputLabel>
                <Select
                  labelId="number-of-answers-select-label"
                  id="number-of-answers-select"
                  value={noOfAnswers}
                  onChange={(e) => setNoOfAnswers(e.target.value)}
                >
                  <MenuItem value={2}>2</MenuItem>
                  <MenuItem value={3}>3</MenuItem>
                  <MenuItem value={4}>4</MenuItem>
                  <MenuItem value={5}>5</MenuItem>
                  <MenuItem value={6}>6</MenuItem>
                </Select>
              </FormControl>
            </div>
            <div>
              <AttachURLTextfield
                placeholder="Attach Youtube URL"
                value={youtubeURL}
                onChange={(e) => updateYoutubeURL(e.target.value)}
                helperText='Format: https://www.youtube.com/watch?v=QJ4g'
                multiline
                rowsMax={3}
              />
            </div>
            <div>
              <UploadImageBox>
                Upload image: {answerPhotoName}
              </UploadImageBox>
              <div>
                <input type="file" id='answer-image-input' onChange={e => { setAnswerImage(e.target.files[0]) }} />
              </div>
              <div>
                <button onClick={(e) => {
                  e.preventDefault();
                  removeAnswerImage();
                }}>
                  Remove Image
                </button>
              </div>
              <AttachOneMessageBox>
                *You can attach only one of either Youtube URL or an image
              </AttachOneMessageBox>
            </div>
          </NewQuestionBox>

          <OuterAnswersBox>
            <InnerAnswersBox>

              <div>Answers:</div>
              <div>Correct answer(s):</div>

              {/* to show all the answers and the selection boxes */}
              {
                answerTexts.map((val, idx) => {
                  return <QuizAnswers
                  key={idx}
                  index={idx}
                  noOfAnswers={noOfAnswers}
                  questionType={questionType}
                  answerTexts={answerTexts}
                  updateAnswers={updateAnswers}
                  singleAnswerValue={singleAnswerValue}
                  setSingleAnswerValue={setSingleAnswerValue}
                  updateMultipleAnswerValues={updateMultipleAnswerValues}
                  />
                })
              }

            </InnerAnswersBox>
          </OuterAnswersBox>

          <AddUpdateButtonBox>
            <Button variant='contained' color='primary' onClick={addQuestion}>
              { pagelocation === 2 ? 'Add Question' : 'Update Question' }
            </Button>
          </AddUpdateButtonBox>
        </form>
      </div>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </div>
  );
}

QuizDetails.propTypes = {
  getQuiz: PropTypes.func,
  qtext: PropTypes.string,
  qtype: PropTypes.string,
  qpoints: PropTypes.number,
  qtime: PropTypes.number,
  qNoOfAnswers: PropTypes.number,
  qAnswers: PropTypes.array,
  qYoutubeURL: PropTypes.string,
  qImageSRC: PropTypes.string,
  qImageName: PropTypes.string
}

export default QuizDetails;
