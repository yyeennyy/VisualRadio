import React from "react";

const Ad = (props) => {
    return (
        <div id = "imgContainer">
            <img id="main_img" alt="main_img" src={props.other}/>
        </div>
    );
}

export default Ad;