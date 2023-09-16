import React from "react";
import YoutubeIframeAPI from './YoutubeIframeAPI';

const Music = (props) => {
    return (
        <div id = "videoContainer">
            <YoutubeIframeAPI videoId={props.other}/>
        </div>
    );
}

export default Music;