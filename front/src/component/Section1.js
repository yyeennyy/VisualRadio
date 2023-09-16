import React from "react";
import Ad from './Ad';
import Ment from './Ment';
import Music from './Music';


const Section1 = (props) => {
    const content = props.content;

    if (content === 'ment') {
        return (
            <Ment other={props.other}/>
        );
    } else if (content === 'ad') {
        return (
            <Ad other={props.other}/>
        );
    } else if (content === 'music') {
        return (
            <Music other={props.other}/>
        );
    }
}

export default Section1;