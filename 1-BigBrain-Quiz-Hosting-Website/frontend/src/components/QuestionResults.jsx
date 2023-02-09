import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const QuestionHeading = styled.div`
  font-weight: bold;
  margin-left: 10px;
`;

const ResultsBox = styled.div`
  display: grid;
  grid-template-columns: 2fr 5fr 2fr 7fr;
  row-gap: 5px;
  column-gap: 20px;
  margin-bottom: 20px;
  margin-left: 20px;

  @media (max-width: 1300px) {
    grid-template-columns: 3fr 5fr 3fr 7fr;
  }

  @media (max-width: 900px) {
    grid-template-columns: 3fr 5fr;
  }
`;

// function to return and display results of each question
function QuestionResults ({ questionNumber, start, answered, type, time, response }) {
  return (
    <>
      <QuestionHeading>
        Question#: {questionNumber}
      </QuestionHeading>
      <ResultsBox>
        <div>
          Started at:
        </div>
        <div>
          {start}
        </div>
        <div>
          Answered at:
        </div>
        <div>
          {answered}
        </div>
        <div>
          Question Type:
        </div>
        <div>
          {type === 'S' ? 'Single answer correct' : 'Multiple answers correct'}
        </div>
        <div>
          Time taken:
        </div>
        <div>
          {time} seconds
        </div>
        <div>
          Response:
        </div>
        <div>
          {response ? 'Correct' : 'Incorrect'}
        </div>
      </ResultsBox>
    </>
  );
}

QuestionResults.propTypes = {
  questionNumber: PropTypes.number,
  start: PropTypes.string,
  answered: PropTypes.string,
  type: PropTypes.string,
  time: PropTypes.number,
  response: PropTypes.bool
};

export default QuestionResults;
