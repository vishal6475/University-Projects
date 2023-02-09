import React from 'react';
import { useHistory } from 'react-router-dom';
import { StoreContext } from '../utils/store';
import styled from 'styled-components';
/*
Plagiarism declaration:
Below 7 images and the youtube video URL have been downloaded from internet and converted to base64.
Just mentioning it so it doesn't cause any plagiarism concerns.
*/
import { NatureMountain } from '../images/NatureMountain.json';
import { NatureLake } from '../images/NatureLake.json';
import { FunnyBaby } from '../images/FunnyBaby.json';
import { FunnyBill } from '../images/FunnyBill.json';
import { FunnyCup } from '../images/FunnyCup.json';
import { FunnyPrecious } from '../images/FunnyPrecious.json';
import { FunnySmith } from '../images/FunnySmith.json';

// declaring styles for the boxes and components on this page and to also allow for responsiveness
const ContainerBox = styled.div`
  width: 80vw;
  margin: auto;
  margin-top: 10px;
`;

const HeadingBox = styled.div`
  background-color: #8b8c8b;
  padding: 5px 10px;
  margin-top: 30px;
`;

const ContentBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const WaitMessage = styled.h3`
  margin-bottom: 0px;
`;

const VideoBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const ImageBox = styled.div`
  margin-left: 23%;
`;

// Main Lobby function
function Lobby () {
  const playerID = localStorage.getItem('playerID');
  const history = useHistory();

  // use state variables to keep track of current page and take actions accordingly
  const context = React.useContext(StoreContext);
  const [showLogout, setShowLogout] = context.showLogout;

  React.useEffect(() => {
    if (showLogout === 1) {
      setShowLogout(0);
    }

    // check for next question every second
    const intervalCheckStatus = setInterval(async () => {
      const fetchPlayerStatus = await fetch(`http://localhost:5005/play/${playerID}/status`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      })

      // if found question, send player to that page
      if (fetchPlayerStatus.status === 200) {
        const playerStatus = await fetchPlayerStatus.json();
        if (playerStatus.started === true) {
          clearInterval(intervalCheckStatus);
          history.push('/player/game');
        }
      }
    }, 500);
  }, []);

  return (
    <ContainerBox>
      <HeadingBox>
        Player lobby
      </HeadingBox>
      <div>
        <ContentBox>
          <WaitMessage>
            Please wait here until the game is being started. Admin will start the game shortly.
          </WaitMessage>
        </ContentBox>
        <ContentBox>
          <h5>
            In the interim, you may enjoy the beautiful natural and funny images shown below!
          </h5>
          <h5>
            You can even watch the latest Fast and Furious 9 trailer here (at the bottom), WOW!!!
          </h5>
        </ContentBox>
        <ImageBox >
          <img src={ NatureMountain } alt="Nature and mountain image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ FunnyBaby } alt="Funny baby image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ FunnyCup } alt="Funny Cup 2020 image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ FunnyBill } alt="Funny bill image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ FunnyPrecious } alt="Funny precious image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ FunnySmith } alt="Funny Will Smith Image" width="70%" />
        </ImageBox>
        <ImageBox>
          <img src={ NatureLake } alt="Nature lake image" width="70%" />
        </ImageBox>
      </div>
      <VideoBox>
        <h3>Fast and Furios 9 trailer:</h3>
        <iframe
          width="60%"
          height="350"
          src={'https://www.youtube.com/embed/SrpgXe_mbFE'}
          frameBorder="0"
          allow="gyroscope;"
          allowFullScreen
          alt="Fast and Furios 9 trailer youtube video"
          title="Fast and Furios 9 trailer youtube video"
        />
      </VideoBox>
    </ContainerBox>
  );
}

export default Lobby;
