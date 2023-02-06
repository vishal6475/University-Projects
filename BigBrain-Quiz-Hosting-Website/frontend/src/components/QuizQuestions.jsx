import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import EditRoundedIcon from '@material-ui/icons/EditRounded';
import DeleteIcon from '@material-ui/icons/Delete';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const Container = styled.div`
  border-style: solid;
  border-radius: 10px;
  border-width: 1px;
  padding: 20px;
  margin-top: 10px;
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

const QuestionIconsBox = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const IconsBox = styled.div`
  display: flex;
  flex-direction: row;
`;

const QuestionBox = styled.div`
  display: grid;
  grid-template-columns: 10fr 60fr 20fr;
  margin-bottom: 3px;
`;

const QuestionTextBox = styled.div`
  max-width: 50vw;
  overflow-wrap: break-word;
`;

const AllDetailsBox = styled.div`
  display: grid;
  grid-template-columns: 10fr 20fr 10fr 20fr 30fr;
  column-gap: 5px;
`;

const YoutubeBox = styled.div`
  max-width: 20vw;
  overflow-wrap: break-word;
`;

// function to return and display details of each question
function QuizQuestions ({ index, question, points, time, type, answers, editQuestion, openModalBox, youtubeURL, imageName }) {
  return (
    <Container>
      <QuestionIconsBox>
        <div>
          Question# {index}
        </div>
        <IconsBox>
          <div value={index} id={index} onClick={ (e) => editQuestion(e.currentTarget.id) } >
            <EditIcon />
          </div>
          <div value={index} id={index} onClick={ (e) => openModalBox(e.currentTarget.id) } >
            <DeleteQuizIcon />
          </div>
        </IconsBox>
      </QuestionIconsBox>
      <QuestionBox>
        <div>
          Question:
        </div>
        <QuestionTextBox>
          {question}
        </QuestionTextBox>
        <div></div>
      </QuestionBox>
      <AllDetailsBox>
        <div>
          Points:
        </div>
        <div>
          {points}
        </div>
        <div></div>
        <div>
          Time to complete:
        </div>
        <div>
          {time} seconds
        </div>
        <div>
          Type:
        </div>
        <div>
          {type === 'S' ? 'Single answer' : 'Multiple answers'}
        </div>
        <div></div>
        <div>
          Number of Answers:
        </div>
        <div>
          {answers}
        </div>
        <div>
          Youtube URL:
        </div>
        <YoutubeBox>
          {youtubeURL.length > 0 ? youtubeURL : 'None'}
        </YoutubeBox>
        <div></div>
        <div>Image Name:</div>
        <div>
          {imageName.length > 0 ? imageName : 'None'}
        </div>
      </AllDetailsBox>
    </Container>
  );
}

QuizQuestions.propTypes = {
  index: PropTypes.number,
  question: PropTypes.string,
  points: PropTypes.number,
  time: PropTypes.number,
  type: PropTypes.string,
  answers: PropTypes.number,
  editQuestion: PropTypes.func,
  openModalBox: PropTypes.func,
  youtubeURL: PropTypes.string,
  imageName: PropTypes.string
};

export default QuizQuestions;
