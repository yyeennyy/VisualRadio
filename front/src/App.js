import { useState, useEffect, useRef } from 'react';
import './App.css';
// import AudioPlayer from 'react-h5-audio-player';
// import 'react-h5-audio-player/lib/styles.css';
import ReactAudioPlayer from 'react-audio-player';
// import { useLocation } from 'react-router-dom';

// npm i axios
import axios from 'axios'; 

// npm i react-router-dom
// import { BrowserRouter } from 'react-router-dom';
// import Routes from './Routes';
// import ScriptData from "./script.json";

import Section1 from './component/Section1';
import Section from './section.json';

// npm i -s react-router-dom

// npm install --save react-audio-player // 이거 말고
// npm i react-h5-audio-player 이거 !

// import Script from "./script.json"

// npm create-react-app api-list

function Logo() {
  return <a href="/">
    <div id = "logo">
        <img id = "logoImg" alt="logo_img" src="images/logo.png"/>
    </div>
  </a>
}

function Data(props) {
  return <div className = "data">
    <div id = "info">{props.radio_name}   {props.date}</div>
    <div className = "search">
        <input type="text" id = "searchBar" placeholder="키워드/사연자 입력"/>
        <img id = "searchButton" alt="searchButton_img" src="images/searchButton.png" onClick={() => {
          console.log("검색버튼 누름");
        }}/>
    </div>
  </div>
}

// Section2 안에 사연자 보여주는 부분은 구현 X
function Section2() {

  const broadcast = 'MBC FM4U';
  const radio_name = '이석훈의 브런치카페';
  const date = '2023-06-18';

  return <div id = "section2">
    <GetScript broadcast={broadcast} radio_name={radio_name} date={date}/>
    {/* <Routes /> */}
    <div id = "index">
        <img id = "opening" alt="opening_img" src="images/opening.png"/>
        <img id = "part1" alt="part1_img" src="images/part1.png"/>
        <img id = "part2" alt="part2_img" src="images/part2.png"/>
    </div>
  </div>
}

// 자동 재생 + ReactAudioPlayer 커스텀 되는지 확인하기
// 원래 Audio 컴포넌트 있던 자리


const GetScript = ({broadcast, radio_name, date}) => {
  const [scriptData, setScriptData] = useState([]);

//   useEffect(() => {
//     fetch("http://localhost:3000")
//     .then(response => {
//       return response.json();
//     })
//     .then(data => {
//       setScriptData(data);
//     });
  axios.get(`/dummy/script.json`)
    .then(response => {
      setScriptData(response.data);
    })
//     .catch(error => {
//       console.error('Error fetching script data:', error);
//     });
// }, [broadcast, radio_name, date]);

  // return <div id = "subtitleContainer">{scriptData}</div>
  return <div id="subtitleContainer">
      {scriptData.map((line, index) => (
        <p key={index} className="scriptLine">
          {line.txt}
        </p>
      ))}
    </div>
}


function App() {
  // const location = useLocation();
  // const searchParams = new URLSearchParams(location.search);

  // const broadcast = searchParams.get('broadcast');
  // const radio_name = searchParams.get('radio_name');
  // const date = searchParams.get('date');

  // const broadcast = 'MBC FM4U';
  const radio_name = '이석훈의 브런치카페';
  const date = '2023-06-18';

  // const [mode, setMode] = useState('PLAY');

  // if (mode === 'PLAY') {

  // } else if (mode === 'PAUSE') {

  // }

  const [currentSection, setCurrentSection] = useState({ content: '', other: '' });
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);

  const updateCurrentTime = () => {
    if (audioRef.current) {
      const newCurrentTime = audioRef.current.audioEl.current.currentTime;
      console.log('현재 재생 시간은 ', newCurrentTime);
      setCurrentTime(newCurrentTime);
    }
  };

  useEffect(() => {

    const foundSection = Section.find((section) => {
      const [start, end] = section.time_range;
      return currentTime >= start && currentTime <= end;
    });

    if (foundSection) {
      console.log('현재 content는 ', foundSection.content);
      // console.log('현재 other은 ', foundSection.other);
      setCurrentSection(foundSection);

      if (foundSection.content === 'music') {
        audioRef.current.audioEl.current.pause();
        clearInterval(updateCurrentTime);
      } else {
        audioRef.current.audioEl.current.play();
        const newInterval = setInterval(updateCurrentTime, 1000);

        return () => {
          clearInterval(newInterval);
        };
      }
    }
  }, [currentTime]);

  return (
    <div className="App">
      <div id = 'wrap'>
        <Logo></Logo>
        <Data radio_name = {radio_name} date = {date}></Data>
        {/* episode 컴포넌트로 구현하려고 했던 부분_s */}
        <div className="episode">
          <div id = "section1"><Section1 content={currentSection.content} other={currentSection.other}/></div>
          <Section2 />
        </div>
        {/* episode 컴포넌트로 구현하려고 했던 부분_e */}
        {/* <Audio src="audio/sum.wav"></Audio>*/}
        <ReactAudioPlayer
          ref={audioRef}
          src="audio/sum.wav" // !!! : 여기 경로 수정
          // autoPlay
          // muted
          controls
        ></ReactAudioPlayer>
      </div>
    </div>
  );
}

export default App;

// <AudioTime></AudioTime>
// <PlayPauseBtn></PlayPauseBtn>


// const GetScript = () => {
//   const [script, setScript] = useState(null);
//   useEffect( () => {
//     axios
//     .get(`/${broadcast}/${radio_name}/${date}/script`)
//     .then( (res) => {
//       setScript(res.data);
//     })
//     .catch( (err) => {
//       console.log('getScript err : ' + err);
//     });
//   }, []);

//   return <div id = "subtitleContainer">
//     {script}
//   </div>
// }