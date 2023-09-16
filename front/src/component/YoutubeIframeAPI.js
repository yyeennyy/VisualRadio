import React from 'react';

// npm install react-youtube
import YouTube from 'react-youtube';

const YoutubeIframeAPI = (props) => {
    const opts = {
        height: '450',
        width: '450',
        playerVars: {
            autoplay: 1,
        },
    };

    const onEnd = () => {
        // 다음 컨텐츠 시작 위치로 이동
    }

    return <YouTube videoId={props.other} opts={opts} onEnd={onEnd}/>
}

export default YoutubeIframeAPI;