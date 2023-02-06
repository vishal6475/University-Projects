import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('to check if the App shows the BigBrain logo', () => {
  render(<App />);
  const linkElement = screen.getByText(/BigBrain/i);
  expect(linkElement).toBeInTheDocument();
});

test('to check if the App shows the Register here link', () => {
  render(<App />);
  const linkElement = screen.getByText(/Register here/i);
  expect(linkElement).toBeInTheDocument();
});
