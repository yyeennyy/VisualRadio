import React, {useState, useEffect} from 'react';

// npm install react-youtube
import YouTube from 'react-youtube';

const YoutubeIframeAPI = (props) => {
    
    const [videoId, setVideoId] = useState('');

    useEffect(() => {
        // props.other이 변경될 때마다 videoId 업데이트
        setVideoId(props.other);
    }, [props.other]);

    const opts = {
        height: '450',
        width: '450',
        playerVars: {
          autoplay: 1,
          origin: 'http://localhost:3000',
        },
      };

    return <YouTube videoId={videoId} opts={opts} />
}

export default YoutubeIframeAPI;