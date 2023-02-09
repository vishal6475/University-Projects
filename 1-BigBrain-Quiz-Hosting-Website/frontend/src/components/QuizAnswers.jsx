import React from 'react';
import TextField from '@material-ui/core/TextField';
import Checkbox from '@material-ui/core/Checkbox';
import Radio from '@material-ui/core/Radio';
import PropTypes from 'prop-types';

// function to return and display answer selection fields for each question
function QuizAnswers ({ index, noOfAnswers, questionType, answerTexts, updateAnswers, singleAnswerValue, setSingleAnswerValue, updateMultipleAnswerValues }) {
  return (
    <>
      {noOfAnswers >= index + 1 &&
      <div>
        <TextField
          label={`Answer ${index + 1}*`}
          onChange={(e) => updateAnswers(index, e.target.value)}
          value={answerTexts[index]}
          multiline
          rowsMax={5}
        />
      </div>
      }

      {questionType === 'M' && noOfAnswers >= index + 1 &&
      <div>
        <Checkbox
          color="primary"
          value={index + 1}
          onChange={(e) => updateMultipleAnswerValues(e)}
          inputProps={{ 'aria-label': 'secondary checkbox' }}
        />
      </div>
      }

      {questionType === 'S' && noOfAnswers >= index + 1 &&
      <div>
        <Radio
          checked={singleAnswerValue === index + 1}
          value={index + 1}
          onClick={(e) => setSingleAnswerValue(parseInt(e.target.value))}
          color='primary'
          name='correct-answer-radio-button'
          inputProps={{ 'aria-label': 'correct-answer' }}
        />
      </div>
      }
    </>
  );
}

QuizAnswers.propTypes = {
  index: PropTypes.number,
  noOfAnswers: PropTypes.number,
  questionType: PropTypes.string,
  answerTexts: PropTypes.array,
  updateAnswers: PropTypes.func,
  singleAnswerValue: PropTypes.number,
  setSingleAnswerValue: PropTypes.func,
  updateMultipleAnswerValues: PropTypes.func
};

export default QuizAnswers;
