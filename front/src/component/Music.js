import React from "react";

// npm install react-youtube
import YouTube from 'react-youtube';

function YoutubeIframeAPI({videoId, onEnd}) {

  const opts = {
    height: '450',
    width: '450',
    playerVars: {
      autoplay: 1,
      origin: 'http://localhost:3000',
    },
  };

  return <YouTube videoId={videoId} opts={opts} onEnd={onEnd}/>
}

const Music = (props) => {

  const onEnd = () => {
    props.youtubeStateCheck(true);
  }

  return (
      <div id = "videoContainer">
          <YoutubeIframeAPI videoId={props.other} onEnd={onEnd}/>
      </div>
  );
}

export default Music;