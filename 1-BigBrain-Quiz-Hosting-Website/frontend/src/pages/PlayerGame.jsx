import React from 'react';
import GameAnswers from '../components/GameAnswers';
import { useParams, useHistory } from 'react-router-dom';
import { StoreContext } from '../utils/store';
import styled from 'styled-components';

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

const QuestionBox = styled.div`
  max-width: 100%;
  overflow-wrap: break-word;
`;

const ShowTimeBox = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const TimeLeftBox = styled.div`
  background-color: yellow;
  width: 105px;
  border-radius: 20px;
  padding: 5px 0 5px 10px;
`;

const TimeLeftUrgentBox = styled.div`
  background-color: #e00202;
  width: 105px;
  border-radius: 20px;
  padding: 5px 0 5px 10px;
  font-weight: bold;
`;

const TimesUpBox = styled.div`
  background-color: #e3e027;
  border-radius: 7px;
  display: flex;
  padding: 5px;
  justify-content: center;
  font-weight: bold;
`;

const ImageVideoBox = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
`;

const GameAnswersBox = styled.div`
  display: grid;
  grid-template-columns: 5fr 5fr;
  row-gap: 30px;
  column-gap: 20px;
  padding: 20px;
`;

const CorrectAnswer = styled.div`
  display: flex;
  justify-content: center;
  color: green;
`;

const InCorrectAnswer = styled.div`
  display: flex;
  justify-content: center;
  color: red;
`;

const CorrectAnswersHeading = styled.div`
  background-color: #32a852;
  border-radius: 7px;
  display: flex;
  padding: 5px;
  margin-top: 10px;
  justify-content: center;
  font-weight: bold;
`;

const CorrectAnswersBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  font-weight: bold;
`;

const CorrectAnswersText = styled.div`
  max-width: 100%;
  overflow-wrap: break-word;
`;

function PlayGame () {
  const params = useParams();
  const history = useHistory();

  // use state variables for this page
  let intervalCheckNextQuestion;
  const playerID = localStorage.getItem('playerID');
  const [currentQuestion, setQuestion] = React.useState('');
  const [questionType, setQuestionType] = React.useState('');
  const [noOfAnswers, setNoOfAnswers] = React.useState(2);
  const [answerTexts, setAnswerTexts] = React.useState(['', '', '', '', '', '']);
  const [singleAnswerValue, setSingleAnswerValue] = React.useState();
  const [multipleAnswerValues, setMultipleAnswerValues] = React.useState([]);
  const [timeLeft, setTimeLeft] = React.useState(0);
  const [isQuizOver, setQuizOver] = React.useState(1);
  const [correctAnswers, setCorrectAnswers] = React.useState([]);
  const [youtubeURL, setYoutubeURL] = React.useState('');
  const [imageSRC, setImageSRC] = React.useState('');

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;

  React.useEffect(() => {
    window.scrollTo(0, 0); // scroll to top of window
    if (showLogout === 1) {
      setShowLogout(0);
    }
    if (params.pid) {
      localStorage.setItem('playerID', params.pid);
    }
    populateQuestion(); // to check and populate question every second
    intervalCheckNextQuestion = setInterval(async () => {
      checkNextQuestion();
    }, 1000);
  }, []);

  // fetch for next question
  const checkNextQuestion = async () => {
    const fetchPlayerQuestion = await fetch(`http://localhost:5005/play/${playerID}/question`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })

    // checking if we got any new question
    if (fetchPlayerQuestion.status === 200) {
      const question = await fetchPlayerQuestion.json();
      const startTime = new Date(question.question.isoTimeLastQuestionStarted);
      const currentTime = new Date();
      const timeLapsed = parseInt((currentTime - startTime) / 1000);
      let timeLeftSeconds = question.question.time - timeLapsed;
      timeLeftSeconds = (timeLeftSeconds >= 0) ? timeLeftSeconds : 0;
      setTimeLeft(timeLeftSeconds);
      if (timeLeftSeconds === 0) {
        setQuizOver(0);
      }
      if (localStorage.getItem('questionStartTime') !== question.question.isoTimeLastQuestionStarted) {
        localStorage.setItem('questionStartTime', question.question.isoTimeLastQuestionStarted);
        setSingleAnswerValue();
        setMultipleAnswerValues([]);
        populateQuestion();
      }
    } else if (fetchPlayerQuestion.status !== 200) {
      clearInterval(intervalCheckNextQuestion);
      history.push('/player/results');
    }
  }

  // function to populate the question details
  const populateQuestion = async () => {
    const fetchPlayerQuestion = await fetch(`http://localhost:5005/play/${playerID}/question`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    })

    // checking for status and loading all the details
    if (fetchPlayerQuestion.status === 200) {
      const question = await fetchPlayerQuestion.json();
      setQuizOver(1);
      setQuestion(question.question);
      setQuestionType(question.question.type);
      if (question.question.youtubeURL.length > 0) {
        setYoutubeURL(question.question.youtubeURL.split('=')[1]);
      } else {
        setYoutubeURL('');
      }
      setImageSRC(question.question.imageSRC);
      const startTime = new Date(question.question.isoTimeLastQuestionStarted);
      const currentTime = new Date();
      const timeLapsed = parseInt((currentTime - startTime) / 1000);
      let timeLeftSeconds = question.question.time - timeLapsed;
      timeLeftSeconds = (timeLeftSeconds >= 0) ? timeLeftSeconds : 0;
      setTimeLeft(timeLeftSeconds);
      setNoOfAnswers(question.question.answers.length);
      const tempAnswers = [...answerTexts];
      for (let i = 0; i < question.question.answers.length; i++) {
        tempAnswers[i] = question.question.answers[i];
      }
      setAnswerTexts(tempAnswers);
      setCorrectAnswers(question.question.correctAnswers);
      localStorage.setItem('questionStartTime', question.question.isoTimeLastQuestionStarted); // to compare with next fetch and see if we got a new question
    } else {
      console.log('Error in getting player question');
    }
  }

  // to keep track of multiple answers selected
  const updateMultipleAnswerValues = (value, checked) => {
    let tempMultipleValues = [];
    if (checked) {
      tempMultipleValues = multipleAnswerValues.concat(parseInt(value));
      tempMultipleValues.sort(function (a, b) { return a - b }); // taken this line from w3schools to sort based on numbers
      setMultipleAnswerValues(tempMultipleValues);
      sendAnswer(tempMultipleValues);
    } else {
      multipleAnswerValues.forEach(eachValue => {
        if (eachValue !== parseInt(value)) {
          tempMultipleValues.push(eachValue);
        }
      })
      tempMultipleValues.sort(function (a, b) { return a - b });
      setMultipleAnswerValues(tempMultipleValues);
      sendAnswer(tempMultipleValues);
    }
  }

  // to submit the answer on each user click
  const submitAnswer = async (qType, value, checked) => {
    if (qType === 'S') {
      setSingleAnswerValue(parseInt(value));
      sendAnswer([parseInt(value)]);
    } else {
      updateMultipleAnswerValues(value, checked);
    }
  }

  // to send the answer to the server
  const sendAnswer = async (answerValues) => {
    const answerDetails = {
      answerIds: answerValues
    };

    // calling fetch to send data
    const fetchSubmitAnswer = await fetch(`http://localhost:5005/play/${localStorage.getItem('playerID')}/answer`, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(answerDetails),
    })

    if (fetchSubmitAnswer.status === 200) {
      console.log('Answer submit successful');
    } else {
      console.log('Error in Answer submit');
    }
  }

  // function to check if two arrays are same
  const isArraysEqual = (arr1, arr2) => {
    if (arr1.length !== arr2.length) {
      return false;
    }
    for (let i = 0; i < arr1.length; i++) {
      let status = false;
      for (let j = 0; j < arr2.length; j++) {
        if (arr1[i] === arr2[j]) {
          status = true;
        }
      }
      if (status === false) {
        return false;
      }
    }
    return true;
  }

  // returning all the game components
  return (
    <ContainerBox fixed>
      <div>
        <HeadingBox>
          Question:
        </HeadingBox>
        <QuestionBox>
          <h2>{currentQuestion.question}</h2>
        </QuestionBox>
        <ImageVideoBox>
          {imageSRC &&
            <img src={imageSRC} alt="Question image for player hint" width="50%"/>
          }
          {youtubeURL &&
            <iframe
              width="50%"
              height="300"
              src={`https://www.youtube.com/embed/${youtubeURL}`}
              frameBorder="0"
              allow="gyroscope;"
              allowFullScreen
              title="Player youtube video for question"
            />
          }
        </ImageVideoBox>
        <ShowTimeBox>
          <div>
            {questionType === 'S' &&
              <div style={{ fontWeight: 'bold' }}>
                Select answer (only one is correct):
              </div>
            }
            {questionType === 'M' &&
              <div style={{ fontWeight: 'bold' }}>
                Select answer(s) (more than one maybe correct):
              </div>
            }
          </div>
          { timeLeft > 9 &&
            <TimeLeftBox>
              Time Left: {timeLeft}s
            </TimeLeftBox>
          }
          { timeLeft <= 9 &&
            <TimeLeftUrgentBox>
              Time Left: {timeLeft}s
            </TimeLeftUrgentBox>
          }
        </ShowTimeBox>
        <div> {/* to show all the answers of a question to select */}
            <GameAnswersBox>
              {
                answerTexts.map((val, idx) => {
                  return <GameAnswers
                  key={idx}
                  index={idx}
                  noOfAnswers={noOfAnswers}
                  questionType={questionType}
                  answerTexts={answerTexts}
                  singleAnswerValue={singleAnswerValue}
                  submitAnswer={submitAnswer}
                  multipleAnswerValues={multipleAnswerValues}
                  timeLeft={timeLeft} />
                })
              }
            </GameAnswersBox>
          </div>
      </div>
      {isQuizOver === 0 &&
        <div> {/* to show the correct answer when time is over */}
          {((questionType === 'S' && singleAnswerValue === correctAnswers[0]) ||
              (questionType === 'M' && isArraysEqual(multipleAnswerValues, correctAnswers))) &&
            <CorrectAnswer>
              <h3>Correct Answer!!</h3>
            </CorrectAnswer>
          }
          {((questionType === 'S' && singleAnswerValue !== correctAnswers[0]) ||
              (questionType === 'M' && !isArraysEqual(multipleAnswerValues, correctAnswers))) &&
            <InCorrectAnswer>
              <h3>Incorrect Answer</h3>
            </InCorrectAnswer>
          }
          <TimesUpBox>
            Time&#39;s Up.
          </TimesUpBox>
          <CorrectAnswersHeading>
            Correct answer(s) are:
          </CorrectAnswersHeading>
          <CorrectAnswersBox> {/* to show all correct answers */}
          {
            answerTexts.map((answer, index) => {
              if (correctAnswers.includes(index + 1)) {
                return (
                <>
                  <CorrectAnswersText>
                    {answer}
                  </CorrectAnswersText>
                </>);
              } else {
                return (<></>);
              }
            })
          }
          </CorrectAnswersBox>
        </div>
      }
    </ContainerBox>
  );
}

export default PlayGame;
