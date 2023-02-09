import React from 'react';
import Header from './components/Header.jsx';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import EditQuiz from './pages/EditQuiz';
import EditQuestion from './pages/EditQuestion';
import JoinPlay from './pages/PlayerJoin';
import Lobby from './pages/PlayerLobby';
import PlayGame from './pages/PlayerGame';
import PlayerResults from './pages/PlayerResults';
import GameResults from './pages/GameResults';
import styled from 'styled-components';
import StoreProvider from './utils/store';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom';

// defining styles for the header, main and footer boxes
const HeaderBox = styled.header`
  height: 39px;
`;

const MainContentBox = styled.main`
  margin-top: 10px;
  min-height: 78vh;
`;

const FooterBox = styled.footer`
  height: 40px;
  margin-top: 50px;
  background-color: #3f51b5;
`;

// In the App, I have mentioned all the possible routes for different pages
function App () {
  return (
    <StoreProvider>
    <Router>
      <HeaderBox>
        <Header/>
      </HeaderBox>
      <MainContentBox>
        <Switch>
          <Route path="/login">
            <Login/>
          </Route>
          <Route path="/register">
            <Register/>
          </Route>
          <Route path="/dashboard">
            <Dashboard/>
          </Route>
          <Route path="/quiz:qid/question:qsid">
            <EditQuestion/>
          </Route>
          <Route path="/quiz:qid">
            <EditQuiz/>
          </Route>
          <Route path="/game/results/:qid/:sid">
            <GameResults/>
          </Route>
          <Route path="/player/join/:sid">
            <JoinPlay/>
          </Route>
          <Route path="/player/join/">
            <JoinPlay/>
          </Route>
          <Route path="/player/lobby">
            <Lobby/>
          </Route>
          <Route path="/player/game/:pid">
            <PlayGame/>
          </Route>
          <Route path="/player/game">
            <PlayGame/>
          </Route>
          <Route path="/player/results">
            <PlayerResults/>
          </Route>
          <Route path="">
            <Dashboard/>
          </Route>
        </Switch>
      </MainContentBox>
      <FooterBox>
      </FooterBox>
    </Router>
    </StoreProvider>
  );
}

export default App;
