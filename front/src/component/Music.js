import React from "react";

import YouTube from 'react-youtube';

function YoutubeIframeAPI({videoId}) {

  const opts = {
    height: '450',
    width: '450',
    playerVars: {
      autoplay: 1,
      origin: 'http://localhost:3000',
    },
  };

  return <YouTube videoId={videoId} opts={opts}/>
}

const Music = (props) => {
    return (
        <div id = "videoContainer">
            <YoutubeIframeAPI videoId={props.other}/>
        </div>
    );
}

export default Music;