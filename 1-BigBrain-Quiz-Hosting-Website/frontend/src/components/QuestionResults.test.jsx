import React from 'react';
import { render, screen } from '@testing-library/react';
import QuestionResults from './QuestionResults';

test('to check if it shows question number as Question#: 5 for input of 5', () => {
  render(<QuestionResults questionNumber={5}/>);
  const linkElement = screen.getByText(/Question#: 5/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows the date as Apr 22 2021 10:07 for the same input of start time', () => {
  render(<QuestionResults start={'Apr 22 2021 10:07'}/>);
  const linkElement = screen.getByText(/Apr 22 2021 10:07/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows the date as Apr 22 2021 10:08 for the same input of answered time', () => {
  render(<QuestionResults answered={'Apr 22 2021 10:08'}/>);
  const linkElement = screen.getByText(/Apr 22 2021 10:08/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows Single answer correct if the input question type is S', () => {
  render(<QuestionResults type={'S'}/>);
  const linkElement = screen.getByText(/Single answer correct/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows Multiple answers correct if the input question type is M', () => {
  render(<QuestionResults type={'M'}/>);
  const linkElement = screen.getByText(/Multiple answers correct/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows time as 100 seconds for input time as 100', () => {
  render(<QuestionResults time={100}/>);
  const linkElement = screen.getByText(/100 seconds/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if it shows incorrect for an answer with response = false', () => {
  render(<QuestionResults response={false}/>);
  const linkElement = screen.getByText(/Incorrect/i);
  expect(linkElement).toBeInTheDocument();
});
