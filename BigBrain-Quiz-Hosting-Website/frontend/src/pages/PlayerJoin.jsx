import React from 'react';
import { useParams, useHistory } from 'react-router-dom';
import Container from '@material-ui/core/Container';
import TextField from '@material-ui/core/TextField';
import { StoreContext } from '../utils/store';
import Button from '@material-ui/core/Button';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import styled from 'styled-components';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const ButtonsBox = styled.div`
  display: grid;
  grid-template-columns: 5fr;
  row-gap: 30px;
  column-gap: 20px;
  margin-top: 20px;
`;

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

function JoinPlay () {
  const params = useParams();
  const history = useHistory();

  // use state variables for this page to use
  const [sessionID, setSessionID] = React.useState('');
  const [playerName, setPlayerName] = React.useState('');

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  React.useEffect(() => {
    // setting the logout and page location to display the components correctly
    if (showLogout === 1) {
      setShowLogout(0);
    }
    if (params.sid) {
      setSessionID(params.sid);
    }
  }, []);

  // functions to show alert messages
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

  // function to verify details and allow a player to join game
  const joinGame = async () => {
    if (sessionID.length === 0) {
      showAlertMessage('warning', 'Please enter the session ID to join game.');
    } else if (playerName.length === 0) {
      showAlertMessage('warning', 'Please enter the name to join game.');
    } else {
      const playerDetails = {
        name: playerName
      };

      // calling fetch to send player to session
      const fetchPlayerJoin = await fetch(`http://localhost:5005/play/join/${sessionID}`, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(playerDetails),
      })

      // checking if the fetch call was successful or not
      if (fetchPlayerJoin.status === 200) {
        const playerJoinDetails = await fetchPlayerJoin.json();
        localStorage.setItem('playerID', playerJoinDetails.playerId);
        history.push('/player/lobby');
      } else { // to show any error messages in case of failure
        showAlertMessage('error', 'Unable to join game. Please check the session ID.');
      }
    }
  }

  // to return all the components
  return (
    <Container component="main" maxWidth="xs">
      <ButtonsBox>
        <div>
          <TextField
            value={sessionID}
            onChange={(e) => setSessionID(e.target.value)}
            variant="outlined"
            margin="normal"
            fullWidth
            label="Game Session Id*"
          />
        </div>
        <div>
          <TextField
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            variant="outlined"
            margin="normal"
            fullWidth
            label="Enter Player Name*"
            autoFocus
          />
        </div>
        <Button
            type="button"
            fullWidth
            variant="contained"
            color="primary"
            onClick={joinGame}
          >
            Join Game
          </Button>
      </ButtonsBox>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default JoinPlay;
