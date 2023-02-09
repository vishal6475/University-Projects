import React from 'react';
import { StoreContext } from '../utils/store';
import styled from 'styled-components';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import { useHistory } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import Breadcrumbs from '@material-ui/core/Breadcrumbs';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import HomeIcon from '@material-ui/icons/Home';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const Container = styled.div`
  height: 39px;
  background-color: #3f51b5;
  padding: 8px 20px 0px 20px;
  position: fixed;
  width: 100vw;
  z-index: 1;

  @media (max-width: 500px) {
    padding: 0;
    padding-top: 8px;
    padding-left: 20px;
    margin-right: 0;
  }
`;

const BigBrainBox = styled.div`
  height: 23px;
  font-weight: bold;
  color: white;
  background-color: transparent;
  border-style: None;
`;

const HeaderBox = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

const HomeIconBox = styled.div`
  padding-top: 2px;
`;

const DashboardBox = styled.div`
  display: flex;
  flex-direction: row;
  padding-top: 2px;
  color: white;
  cursor: pointer;
`;

const LogoutButton = styled.button`
  margin-right: 50px;
  background-color: #454343;
  color: white;
  border-radius: 4px;
  border-width: 0;
  cursor: pointer;
`;

const EditQuiz = styled.div`
  color: #bdbdbd;

  @media (max-width: 500px) {
    display: none;
  }
`;

const EditQuizLink = styled.div`
  color: white;
  cursor: pointer;

  @media (max-width: 500px) {
    display: none;
  }
`;

const EditQuestion = styled.div`
  color: #bdbdbd;

  @media (max-width: 650px) {
    display: none;
  }
`;

const GameResults = styled.div`
  color: #bdbdbd;

  @media (max-width: 650px) {
    display: none;
  }
`;

// classes for Material UI components- can't convert them to styled components as they use some internal Material UI styles
const useStyles = makeStyles((theme) => ({
  root: {
    '& > * + *': {
      marginTop: theme.spacing(2),
    },
  },
}));

// function to show alerts
function Alert (props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

// Main Header function
function Header () {
  const classes = useStyles();
  const history = useHistory();

  // use state variables to keep track of page location and display some components (like logout button) accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;
  const [pagelocation, setPageLocation] = context.pagelocation;

  // use state variables to show alert messages
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    // setting the page locations
    setShowLogout(showLogout);
    setPageLocation(pagelocation);
  }, []);

  // functions to show alert messages
  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  };

  // function to logout an user via calling fetch
  const logout = async () => {
    const logoutUser = await fetch('http://localhost:5005/admin/auth/logout', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    // checking if the fetch call was successful or not
    if (logoutUser.status === 200) {
      localStorage.removeItem('token');
      history.push('/login');
    } else { // to show any error messages in case of failure
      setOpen(true);
    }
  }

  // to transfer to dashboard page on clicking dashboard icon
  const loadDashboard = async () => {
    history.push('/dashboard');
    window.scrollTo(0, 0);
  }

  // to transfer to quiz edit page page on clicking quiz edit icon
  const loadEditQuizPage = async () => {
    history.push(`/quiz${localStorage.getItem('quiz_id')}`);
    window.scrollTo(0, 0);
  }

  // to return and show the header of each page
  return (
    <Container>
      <HeaderBox>
        <div>
          <BigBrainBox>
            BigBrain
          </BigBrainBox>
        </div>
        <div className={classes.root}>
          {/* to show appropriate navigations links for dashboard, edit quiz and edit questions pages */}
          <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb">
            { (pagelocation === 1 || pagelocation === 2 || pagelocation === 3 || pagelocation === 4) &&
              <DashboardBox onClick={loadDashboard}>
                <HomeIconBox>
                  {<HomeIcon fontSize='small' alt='HomePage icon for dashboard' />}
                </HomeIconBox>
                <div>Dashboard</div>
              </DashboardBox>
            }
            { pagelocation === 3 &&
              <EditQuizLink onClick={loadEditQuizPage} >
                Edit Quiz
              </EditQuizLink>
            }
            { pagelocation === 2 &&
              <EditQuiz>
                Edit Quiz
              </EditQuiz>
            }
            { pagelocation === 3 &&
              <EditQuestion>
                Edit Question
              </EditQuestion>
            }
            { pagelocation === 4 &&
              <GameResults>
                Game Results
              </GameResults>
            }
          </Breadcrumbs>
        </div>
        <div>
          {(showLogout === 1) &&
            <div>
              <LogoutButton onClick={logout}>
                Logout
              </LogoutButton>
            </div>
          }
        </div>
      </HeaderBox>

      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="error">
          Logout failed due to invalid token. Your auth token may have expired.
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default Header;
