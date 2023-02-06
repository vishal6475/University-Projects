import React from 'react';
import BarChart from 'react-bar-chart';
import PropTypes from 'prop-types';
import styled from 'styled-components';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const BarChartBox = styled.div`
  display: flex;
  justify-content: center;
`;

// function to show the bar chart on the basis of received data
function ResultsBarChart ({ data }) {
  if (!data) { // if there is delay in receiving data, we can use below data so that component doesn't give any error
    data = [
      { text: '1', value: 100 },
      { text: '2', value: 0 },
      { text: '3', value: 0 },
      { text: '4', value: 0 },
      { text: '5', value: 0 },
      { text: '6', value: 0 },
      { text: '7', value: 0 },
      { text: '8', value: 0 },
      { text: '9', value: 0 },
      { text: '10', value: 0 }
    ];
  }
  return (
    <BarChartBox>
      <BarChart
        height={300}
        width={330}
        data={data}
        margin={{ top: 20, right: 20, bottom: 30, left: 40 }}
      />
    </BarChartBox>
  );
}

ResultsBarChart.propTypes = {
  data: PropTypes.array
}

export default ResultsBarChart;
