import React from 'react';
import { render, screen } from '@testing-library/react';
import QuizQuestions from './QuizQuestions';

test('to check if the component shows None for youtube URL if it was not entered and image was entered', () => {
  render(<QuizQuestions youtubeURL='' imageName='Any' />);
  const linkElement = screen.getByText(/None/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if the component shows name of the image if it was provided', () => {
  render(<QuizQuestions youtubeURL='' imageName='Mountain.jpg' />);
  const linkElement = screen.getByText(/Mountain/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if the component shows None for image if it was not entered and youtubeURL was entered', () => {
  render(<QuizQuestions youtubeURL='https://www.youtube.com/watch?v=bBRAseMeAIU' imageName='' />);
  const linkElement = screen.getByText(/None/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if the component shows only the main id of youtube url (after splitting) if the whole URL is entered', () => {
  render(<QuizQuestions youtubeURL='https://www.youtube.com/watch?v=bBRAseMeAIU' imageName='' />);
  const linkElement = screen.getByText(/bBRAseMeAIU/i);
  expect(linkElement).toBeInTheDocument();
});
