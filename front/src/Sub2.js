import { useState, useEffect, useRef } from 'react';
import './Sub2.css';
// import AudioPlayer from 'react-h5-audio-player';
// import 'react-h5-audio-player/lib/styles.css';

// npm install --save react-audio-player
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
// npm install react-audio-player
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
function Section2(props) {

  const broadcast = 'MBC FM4U';
  const radio_name = '이석훈의 브런치카페';
  const date = '2023-06-18';

  return <div id = "section2">
    <GetScript broadcast={broadcast} radio_name={radio_name} date={date} audioRef={props.audioRef}/>
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

const handleTextClick = (time, audioRef) => {
  const [minutes, seconds] = time.split(':').map(parseFloat);
  const totalTimeInSeconds = minutes * 60 + seconds;

  if (audioRef.current) {
    audioRef.current.audioEl.current.currentTime = totalTimeInSeconds;
  }
};

const GetScript = (props) => {
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
        <p 
          key={index}
          className="scriptLine"
          onClick={() => handleTextClick(line.time, props.audioRef)}  
        >
          {line.txt}
        </p>
      ))}
    </div>
}


function Sub2() {
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

  const [currentSection, setCurrentSection] = useState({ content: '', time_range: [0, 0], other: '' });
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);
  const [nextCurrentSection, setNextCurrentSection] = useState({ content: '', time_range: [0, 0], other: '' });
  const [audioPlaying, setAudioPlaying] = useState(false); 
  const [youtubeStateEnd, setYoutubeStateEnd] = useState(true);

  // 현재 재생 시간 반환
  const updateCurrentTime = () => {
    if (audioRef.current) {
      const newCurrentTime = audioRef.current.audioEl.current.currentTime;
      console.log('현재 재생 시간은 ', newCurrentTime);
      setCurrentTime(newCurrentTime);
    }
  };

  // ReactAudioPlayer가 재생될 때 호출되는 함수
  const handleAudioPlay = () => {
    setAudioPlaying(true); // 오디오 재생 중 상태로 설정
    // audioRef.current.audioEl.current.play(); // 이거 잠시 추가
  };

  // ReactAudioPlayer가 일시 정지될 때 호출되는 함수
  const handleAudioPause = () => {
    setAudioPlaying(false); // 오디오 일시 정지 상태로 설정
    // audioRef.current.audioEl.current.pause(); // 이거 잠시 추가
  };

  // currentTime 기준으로 다음 content를 찾아서 반환하는 함수
  const findNextContent = (currentTime) => {
    const foundSection = Section.find((section) => {
      const [start, end] = section.time_range;
      return currentTime >= start && currentTime <= end;
    });

    if (foundSection) {
      const currentIndex = Section.indexOf(foundSection);
      setNextCurrentSection(Section[currentIndex + 2]);
      console.log('다음 content는', nextCurrentSection);
      console.log('다음 content의 시작 시간은 ', nextCurrentSection.time_range[0]);
      return nextCurrentSection;
    }
  };

  // 유튜브 영상이 재생 중인지, 아닌지 확인하는 함수
  const youtubeStateCheck = youtubeStateEnd => {
    setYoutubeStateEnd(youtubeStateEnd);
  }

  // 유튜브 영상이 끝나면 다음 content 시작 위치로 이동해서 재생
  useEffect(() => {
    // 유튜브 영상 재생이 끝났다면 ...
    if (youtubeStateEnd) {

      setCurrentSection(findNextContent(currentTime));
      console.log('다음 contents', findNextContent(currentTime));
      // 다음 content를 찾아서
      // const next = findNextContent(currentTime);
      // console.log('next는 ', next);

      // 현재 content로 set => 결국 next가 currentSection이 되어 있어야 함
      // setCurrentSection(next); // 적용이 안됨.. ㅠㅠㅠ
    

      // setCurrentSection(next, () => {
      //   console.log('성공?');
      // });
      
      // console.log('currentSection은', currentSection);
      // useEffect(() => console.log(currentSection), currentSection)

      // 다음 content의 시작 시간으로 ReactAudioPlayer 위치 이동
      if (findNextContent(currentTime).time_range) {
        audioRef.current.audioEl.current.currentTime = findNextContent(currentTime).time_range[0];
        setCurrentTime(findNextContent(currentTime).time_range[0] + 0.5); // 눈물 광광 ...
      }

      setAudioPlaying(true);
      
      // audioRef.current.audioEl.current.play();
    
    }
  }, [youtubeStateEnd]);

  // const handleMusicEnd = () => {
  //   // 유튜브 영상이 끝날 때 호출되는 콜백 함수
  //   // currentSection을 nextCurrentSection으로 업데이트하고 ReactAudioPlayer를 재생합니다.
  //   setCurrentSection(nextCurrentSection);
  //   audioRef.current.audioEl.current.play();
  // };
  
  // useEffect(() => {

  //   const foundSection = Section.find((section) => {
  //     const [start, end] = section.time_range;
  //     return currentTime >= start && currentTime <= end;
  //   });

  //   if (foundSection) {
  //     console.log('현재 content는 ', foundSection.content);
  //     // console.log('현재 other은 ', foundSection.other);
  //     setCurrentSection(foundSection);

  //     if (foundSection.content === 'music') {

  //       const currentIndex = Section.indexOf(foundSection);
  //       const nextSection = Section[currentIndex + 1];

  //       if (nextSection) {
  //         // 다음 섹션의 시작 시간을 가져옵니다.
  //         setNextSectionStartTime(nextSection.time_range[0]);
  //         console.log('다음 content의 시작 시간은 ', nextSectionStartTime);
  //       } else {
  //         console.log('다음 섹션 없음');
  //       }
  //       audioRef.current.audioEl.current.pause();

  //       audioRef.current.audioEl.current.currentTime = nextSectionStartTime;
  //       clearInterval(updateCurrentTime);
  //     } else {
  //       audioRef.current.audioEl.current.play();
  //       const newInterval = setInterval(updateCurrentTime, 1000);

  //       return () => {
  //         clearInterval(newInterval);
  //       };
  //     }
  //   }
  // }, [currentTime, nextSectionStartTime]);



  // 해당 과정은 currentTime(현재 재생 시간)과 audioPlaying(오디오 재생 여부)이 바뀔 때마다 실행됨
  // ReactAudioPlayer가 재생 중이면
  // 1. 현재 재생 시간에 해당하는 content(=foundSection) 찾기
  // 2. foundSection을 찾으면 현재 content로 설정
  // 3. content가 music, ad / ment 중에 어디에 속하는지 비교하여
  // 3-1. music이면, ReactAudioPlayer 정지 + 유튜브 재생 상태 설정 + clearInterval
  // 3-2. ment나 ad이면, ReactAudioPlayer 재생 + setInterval(1초마다 현재 재생시간 반환)
  useEffect(() => {
    if (audioPlaying) {
      // 현재 content(=foundSection) 찾고
      const foundSection = Section.find((section) => {
        const [start, end] = section.time_range;
        return currentTime >= start && currentTime <= end;
      });

      if (foundSection) {
        console.log('현재 content는 ', foundSection.content);
        // console.log('현재 other은 ', foundSection.other);
        setCurrentSection(foundSection);

        // 현재 content가 music이면
        // ReactAudioPlayer 정지 + setYoutubeStateEnd(false)
        if (foundSection.content === 'music') {

          // const currentIndex = Section.indexOf(foundSection);
          // const nextSection = Section[currentIndex + 1];
          // const nextSection = findNextContent(currentTime);

          // if (nextSection) {
          //   setNextCurrentSection(nextSection);
          //   setNextSectionStartTime(nextSection.time_range[0]);
            
          //   console.log('다음 content는 ', nextCurrentSection.content);
          //   console.log('다음 content의 시작 시간은 ', nextSectionStartTime);
          // } else {
          //   console.log('다음 섹션 없음');
          // }

          audioRef.current.audioEl.current.pause();
          setYoutubeStateEnd(false);
          clearInterval(updateCurrentTime);
        } else if (foundSection.content === 'ad' || foundSection.content === 'ment') { 
          audioRef.current.audioEl.current.play();
          const newInterval = setInterval(updateCurrentTime, 1000);

          return () => {
            clearInterval(newInterval);
          };
        }
      }
    }
  }, [audioPlaying, currentTime]);

  return (
    <div className="Sub2">
      <div id = 'wrap'>
        <Logo></Logo>
        <Data radio_name = {radio_name} date = {date}></Data>
        {/* episode 컴포넌트로 구현하려고 했던 부분_s */}
        <div className="episode">
          <div id = "section1">
            <Section1
              content={currentSection.content}
              other={currentSection.other}
              youtubeStateCheck={youtubeStateCheck}
              />
          </div>
          <Section2 audioRef={audioRef} />
        </div>
        {/* episode 컴포넌트로 구현하려고 했던 부분_e */}
        {/* <Audio src="audio/sum.wav"></Audio>*/}
        <ReactAudioPlayer
          ref={audioRef}
          src="audio/sum.wav" // !!! : 여기 경로 수정해야 함
          // autoPlay
          // muted
          controls
          onPlay={handleAudioPlay}
          onPause={handleAudioPause}
        ></ReactAudioPlayer>
      </div>
    </div>
  );
}

export default Sub2;




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