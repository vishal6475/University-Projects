import React from 'react';
import Checkbox from '@material-ui/core/Checkbox';
import Radio from '@material-ui/core/Radio';
import PropTypes from 'prop-types';
import styled from 'styled-components';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const AnswerBox = styled.div`
  width: 100%;
  border-style: solid;
  background-color: #a85732;
  border-radius: 10px;
  border-width: 1px;
  display: grid;
  grid-template-columns: 5fr 2fr;
`;

const AnswerTextBox = styled.div`
  padding: 7px 0 0 6px;
  max-width: 25vw;
  overflow-wrap: break-word;
`;

// Main function GameAnswers to return all the components of the answers
function GameAnswers ({ index, noOfAnswers, questionType, answerTexts, singleAnswerValue, submitAnswer, multipleAnswerValues, timeLeft }) {
  return (
    <>
    {noOfAnswers >= index + 1 &&
      <AnswerBox>
        <AnswerTextBox>
          {answerTexts[index]}
        </AnswerTextBox>

        {questionType === 'M' &&
        <div>
          <Checkbox
            color="primary"
            disabled={timeLeft === 0}
            checked={multipleAnswerValues.includes(index + 1)}
            value={index + 1}
            onChange={(e) => submitAnswer('M', e.target.value, e.target.checked)}
            inputProps={{ 'aria-label': 'select answers checkbox' }}
          />
        </div>
        }

        {questionType === 'S' &&
        <div>
          <Radio
            checked={singleAnswerValue === index + 1}
            value={index + 1}
            disabled={timeLeft === 0}
            onClick={(e) => submitAnswer('S', e.target.value) }
            color='primary'
            name='correct-answer-radio-button'
            inputProps={{ 'aria-label': 'select answer radio button' }}
          />
        </div>
        }
      </AnswerBox>
    }
    </>
  );
}

GameAnswers.propTypes = {
  index: PropTypes.number,
  noOfAnswers: PropTypes.number,
  questionType: PropTypes.string,
  answerTexts: PropTypes.array,
  updateAnswers: PropTypes.func,
  singleAnswerValue: PropTypes.number,
  submitAnswer: PropTypes.func,
  multipleAnswerValues: PropTypes.array,
  timeLeft: PropTypes.number
};

export default GameAnswers;
