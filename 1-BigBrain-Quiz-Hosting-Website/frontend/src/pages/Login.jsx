import React from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import { Link, useHistory } from 'react-router-dom';
import { StoreContext } from '../utils/store';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';

// classes for Material UI components- can't convert them to styled components as they use some internal Material UI styles
const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  form: {
    width: '100%',
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// Main login function
function Login () {
  // variables for accessing Material UI classes and history paths
  const classes = useStyles();
  const history = useHistory();

  // use state variables for this login page
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertSeverity, setAlertSeverity] = React.useState('');

  // use state variables to keep track of page location and display some components (like logout button) accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

  React.useEffect(() => {
    // setting the logout and page location to display the components correctly
    if (showLogout === 1) {
      setShowLogout(0);
    }
    if (pagelocation !== 0) {
      setPageLocation(0);
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

  // function to check the inputs and login the user
  async function signIn () {
    // to check if email and password have been entered or not
    if (email.length === 0) {
      showAlertMessage('warning', 'Please enter the email to login.');
    } else if (password.length === 0) {
      showAlertMessage('warning', 'Please enter the password to login.');
    } else { // if all details are entered, allow the user to login
      const userDetails = {
        email: email,
        password: password
      };

      // calling fetch to login the user
      const loginUser = await fetch('http://localhost:5005/admin/auth/login', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userDetails),
      })

      // checking if login is successful or failed
      if (loginUser.status === 200) {
        const data = await loginUser.json();
        localStorage.setItem('token', data.token); // store the auth token obtained after login
        history.push('/dashboard');
      } else { // to show any error
        const errorResponse = await loginUser.json();
        showAlertMessage('error', `Login failed. ${errorResponse.error}.`);
      }
    }
  }

  // returing the login page
  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Avatar>
        </Avatar>
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <form className={classes.form} noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            name="email"
            label="Email Address"
            autoComplete="email"
            autoFocus
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="password"
            name="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="button"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
            onClick={signIn}
          >
            Login
          </Button>
          <Grid container>
            <Grid item xs>
            </Grid>
            <Grid item>
              <Link to="/register" variant="body2">
                {"Don't have an account? Register here"}
              </Link>
            </Grid>
          </Grid>
        </form>
      </div>

      {/* to show popups for success, error, warning or info alerts */}
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity={alertSeverity}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default Login;
