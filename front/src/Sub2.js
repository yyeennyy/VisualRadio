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

function timeStringToFloat(time) {
  const [minutes, seconds] = time.split(':').map(parseFloat);
  return minutes * 60 + seconds;
}

// Section2 안에 사연자 보여주는 부분은 구현 X
function Section2(props) {
  const script = props.scriptData;
  const audioRef = props.audioRef;

  // 초기값 -1로 설정 => 아무것도 강조하지 않도록
  // const [highlightedIndex, setHighlightedIndex] = useState(-1);
  let subtitlesWithTime = '';
  const [highlightedSubtitleIndex, setHighlightedSubtitleIndex] = useState(-1);

  // 자막 클릭 시, 오디오 이동
  const handleSubtitleClick = (time, index) => {
    if (props.currentSection.content === 'music') {
      props.youtubeStateCheck(true);
    }

    if (props.audioRef.current) {
      props.audioRef.current.audioEl.current.currentTime = time;
    }

    setHighlightedSubtitleIndex(index);

    const subtitleContainer = document.getElementById("subtitleContainer");
    const highlightedSubtitle = subtitleContainer.children[index];
    const containerTop = subtitleContainer.getBoundingClientRect().top;
    const highlightedSubtitleTop = highlightedSubtitle.getBoundingClientRect().top - containerTop;
    const subtitleHeight = highlightedSubtitle.getBoundingClientRect().height;
    const containerHeight = subtitleContainer.getBoundingClientRect().height;
  
    const scrollAmount = highlightedSubtitleTop - containerTop - (containerHeight - subtitleHeight) / 2;
    subtitleContainer.scrollTo({
      top: subtitleContainer.scrollTop + scrollAmount,
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    // scriptData를 사용하여 자막을 화면에 표시
    const subtitleContainer = document.getElementById("subtitleContainer");
    subtitleContainer.innerHTML = ''; // 이전 자막을 초기화

    subtitlesWithTime = script.map(subtitle => ({
      txt: subtitle.txt,
      time: timeStringToFloat(subtitle.time)
    }));

    subtitlesWithTime.forEach((subtitle, index) => {
      const block = document.createElement('div');
      block.className = 'subtitle';
      block.innerText = subtitle.txt;
      block.addEventListener('click', () => {
        handleSubtitleClick(subtitle.time, index);
      });

      // if (audioRef.current && audioRef.current.audioEl.current.currentTime + 0.5 >= timeToSeconds(subtitle.time) && audioRef.current.audioEl.current.currentTime - 0.5 <= timeToSeconds(subtitle.time)) {
      //   block.style.fontWeight = '900';
      //   setHighlightedIndex(index); // 강조된 라인의 인덱스 업데이트
      // }

      subtitleContainer.appendChild(block);
    });

    const audioEl = audioRef.current.audioEl.current;
    const handleTimeUpdate = () => {
      const currentTime = audioEl.currentTime;
      for (let i = 0; i < subtitlesWithTime.length; i++) {
        const subtitle = subtitlesWithTime[i];
        const nextSubtitle = subtitlesWithTime[i + 1];
        if (nextSubtitle && nextSubtitle.time <= currentTime) {
          continue;
        }
        if (subtitle.time <= currentTime) {
          // Highlight the current subtitle
          subtitleContainer.children[i].style.fontWeight = 'bold';
          setHighlightedSubtitleIndex(i);
        } else {
          subtitleContainer.children[i].style.fontWeight = 'normal';
        }
      }
      // Reset styles for other subtitles
      if (highlightedSubtitleIndex !== -1) {
        for (let i = 0; i < subtitlesWithTime.length; i++) {
          if (i !== highlightedSubtitleIndex) {
            subtitleContainer.children[i].style.fontWeight = 'normal';
          }
        }
      }

      if (highlightedSubtitleIndex !== -1) {
        const highlightedSubtitle = subtitleContainer.children[highlightedSubtitleIndex];
        const containerTop = subtitleContainer.getBoundingClientRect().top;
        const highlightedSubtitleTop = highlightedSubtitle.getBoundingClientRect().top - containerTop;
        const subtitleHeight = highlightedSubtitle.getBoundingClientRect().height;
        const containerHeight = subtitleContainer.getBoundingClientRect().height;
    
        // 스크롤 위치를 계산하여 중앙에 오도록 조정합니다.
        const scrollAmount = highlightedSubtitleTop - containerTop - (containerHeight - subtitleHeight) / 2;
        subtitleContainer.scrollTo({
          top: subtitleContainer.scrollTop + scrollAmount,
          behavior: 'smooth',
        });
      }
    };

    audioEl.addEventListener('timeupdate', handleTimeUpdate);

    return () => {
      audioEl.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, [script, audioRef, highlightedSubtitleIndex]);



  return <div id = "section2">
    <div id = "subtitleContainer">{props.script}</div>
    <div id = "index">
        <img id = "opening" alt="opening_img" src="images/opening.png"/>
        <img id = "part1" alt="part1_img" src="images/part1.png"/>
        <img id = "part2" alt="part2_img" src="images/part2.png"/>
    </div>
  </div>
}


// 자동 재생 + ReactAudioPlayer 커스텀 되는지 확인하기
// 원래 Audio 컴포넌트 있던 자리

// const handleTextClick = (time, audioRef) => {
//   // 시간을 분:초 형식에서 초로 변환
//   const [minutes, seconds] = time.split(':').map(parseFloat);
//   const totalTimeInSeconds = minutes * 60 + seconds;

//   if (audioRef.current) {
//     audioRef.current.audioEl.current.currentTime = totalTimeInSeconds;
//   }
// };

// const GetScript = (props) => {
//   const [scriptData, setScriptData] = useState([]);

//   useEffect(() => {
//     axios.get(`/dummy/script.json`)
//       .then(response => {
//         setScriptData(response.data);
//       });
//   }, []);

//   return <div id = "subtitleContainer">{scriptData}</div>;
// }

  // useEffect(() => {
  //   // Add a listener to the audio element to track the current time
  //   const audioEl = props.audioRef.current.audioEl.current;
    
  //   const handleTimeUpdate = () => {
  //     const currentTime = audioEl.currentTime;
      
  //     // Find the script line that matches the current time
  //     const matchedLine = scriptData.find((line) => {
  //       const [minutes, seconds] = line.time.split(':').map(parseFloat);
  //       const lineTimeInSeconds = minutes * 60 + seconds;
  //       return currentTime >= lineTimeInSeconds;
  //     });

  //     // Scroll to the matched script line
  //     if (matchedLine) {
  //       const element = document.getElementById(`line-${matchedLine.time}`);
  //       if (element) {
  //         element.scrollIntoView({ behavior: 'smooth' });
  //       }
  //     }
  //   };

  //   audioEl.addEventListener('timeupdate', handleTimeUpdate);

  //   return () => {
  //     audioEl.removeEventListener('timeupdate', handleTimeUpdate);
  //   };
  // }, [scriptData, props.audioRef]);

//   useEffect(() => {
//     fetch("http://localhost:3000")
//     .then(response => {
//       return response.json();
//     })
//     .then(data => {
//       setScriptData(data);
//     });

  // axios.get(`/dummy/script.json`)
  //   .then(response => {
  //     setScriptData(response.data);
  //   })

//     .catch(error => {
//       console.error('Error fetching script data:', error);
//     });
// }, [broadcast, radio_name, date]);

  // return <div id = "subtitleContainer">{scriptData}</div>
//   return <div id="subtitleContainer">
//       {scriptData.map((line, index) => (
//         <p
//           key={index}
//           id={`line-${line.time}`}
//           className="scriptLine"
//           onClick={() => handleTextClick(line.time, props.audioRef)}
//         >
//           {line.txt}
//         </p>
//       ))}
//     </div>
// }


function Sub2() {
  // const location = useLocation();
  // const searchParams = new URLSearchParams(location.search);

  // const broadcast = searchParams.get('broadcast');
  // const radio_name = searchParams.get('radio_name');
  // const date = searchParams.get('date');

  // const broadcast = 'MBC FM4U';
  const radio_name = '이석훈의 브런치카페';
  const date = '2023-06-18';

  const [currentSection, setCurrentSection] = useState({ content: '', time_range: [0, 0], other: '' });
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);
  const [audioPlaying, setAudioPlaying] = useState(false); 
  const [youtubeStateEnd, setYoutubeStateEnd] = useState(true);
  const [foundSection, setFoundSection] = useState({ content: '', time_range: [0, 0], other: '' });

  const [scriptData, setScriptData] = useState([]);

  useEffect(() => {
    axios.get(`/dummy/script.json`)
    .then(response => {
      setScriptData(response.data);
    });
  }, []);

  // 현재 재생 시간 반환
  const updateCurrentTime = () => {
    if (audioRef.current) {
      const newCurrentTime = audioRef.current.audioEl.current.currentTime;
      console.log('현재 재생 시간은 ', newCurrentTime);
      setCurrentTime(newCurrentTime);
    }
  };

  // const handleAudioListen = (e) => {
  //   console.log('e는 ', e);
  //   const newCurrentTime = e.target.currentTime;
  //   console.log('현재 재생 시간은 ', newCurrentTime);
  //   setCurrentTime(newCurrentTime);

  //   const foundSection = Section.find((section) => {
  //     const [start, end] = section.time_range;
  //     return newCurrentTime >= start && newCurrentTime <= end;
  //   });

  //   if (foundSection) {
  //     setCurrentSection(foundSection);
  //   }
  // };

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

  // 유튜브 영상이 재생 중인지, 아닌지 확인하는 함수
  const youtubeStateCheck = youtubeStateEnd => {
    setYoutubeStateEnd(youtubeStateEnd);
  }

  // 유튜브 영상이 끝나면 다음 content 시작 위치로 이동해서 재생
  useEffect(() => {
    // 유튜브 영상 재생이 끝났다면 youtubeStateEnd = true
    if (youtubeStateEnd) {

      setCurrentTime(currentTime + 0.5);

      setFoundSection(Section.find((section) => {
        const [start, end] = section.time_range;
        return currentTime >= start && currentTime <= end;
      }));

      setCurrentSection(foundSection);
      console.log('1. 현재 currentSection은 ', currentSection);
      // setCurrentTime(currentSection.time_range[1] + 0.5); // 눈물 광광 ...
      console.log('2. 현재 current time은 ', currentTime);
      audioRef.current.audioEl.current.currentTime = currentSection.time_range[1];
      setCurrentTime(currentSection.time_range[1] + 0.5); // 눈물 광광 ...
      setFoundSection(Section.find((section) => {
        const [start, end] = section.time_range;
        return currentTime >= start && currentTime < end;
      }));
      console.log('3. foundSection은 ', foundSection);
      setCurrentSection(foundSection);
      console.log('4. 현재 currentSection은 ', currentSection);
      setCurrentTime(currentSection.time_range[0]);
      console.log('5. 현재 currentTime은 ', currentTime);
      setFoundSection(Section.find((section) => {
        const [start, end] = section.time_range;
        return currentTime >= start && currentTime <= end;
      }));
      console.log('6. 현재 foundSection : ', foundSection);
      setAudioPlaying(true);
      
      // audioRef.current.audioEl.current.play();
    } else {
      setFoundSection(Section.find((section) => {
        const [start, end] = section.time_range;
        return currentTime >= start && currentTime <= end;
      }));
      setCurrentSection(foundSection);
      audioRef.current.audioEl.current.currentTime = currentSection.time_range[1];
      setCurrentTime(currentSection.time_range[1] + 0.5); // 눈물 광광 ...
    }
  }, [youtubeStateEnd]);


  // 해당 과정은 currentTime(현재 재생 시간)과 audioPlaying(오디오 재생 여부)이 바뀔 때마다 실행됨
  // ReactAudioPlayer가 재생 중이면
  // 1. 현재 재생 시간에 해당하는 content(=foundSection) 찾기
  // 2. foundSection을 찾으면 현재 content로 설정
  // 3. content가 music, ad / ment 중에 어디에 속하는지 비교하여
  // 3-1. music이면, ReactAudioPlayer 정지 + 유튜브 재생 상태 설정 + clearInterval
  // 3-2. ment나 ad이면, ReactAudioPlayer 재생 + setInterval(1초마다 현재 재생시간 반환)
  // useEffect(() => {
  //   if (audioPlaying) {
      
  //     const foundSection = Section.find((section) => {
  //       const [start, end] = section.time_range;
  //       return currentTime >= start && currentTime <= end;
  //     });

  //     if (foundSection) {
  //       console.log('현재 content는 ', foundSection.content);
  //       // console.log('현재 other은 ', foundSection.other);
  //       setCurrentSection(foundSection);

  //       if (foundSection.content === 'music') {

  //         // const currentIndex = Section.indexOf(foundSection);
  //         // const nextSection = Section[currentIndex + 1];
  //         // const nextSection = findNextContent(currentTime);

  //         // if (nextSection) {
  //         //   setNextCurrentSection(nextSection);
  //         //   setNextSectionStartTime(nextSection.time_range[0]);
            
  //         //   console.log('다음 content는 ', nextCurrentSection.content);
  //         //   console.log('다음 content의 시작 시간은 ', nextSectionStartTime);
  //         // } else {
  //         //   console.log('다음 섹션 없음');
  //         // }

  //         audioRef.current.audioEl.current.pause();
  //         setYoutubeStateEnd(false);
  //         clearInterval(updateCurrentTime);
  //       } else if (foundSection.content === 'ad' || foundSection.content === 'ment') { 
  //         audioRef.current.audioEl.current.play();
  //         const newInterval = setInterval(updateCurrentTime, 1000);

  //         return () => {
  //           clearInterval(newInterval);
  //         };
  //       }
  //     }
  //   }
  // }, [audioPlaying, currentTime]);

  // 아래 코드는 위의 코드를 useEffect 부분과 함수 부분으로 분리한 후 코드 수정 진행함
  const foundCurrentContent = () => {
    setFoundSection(Section.find((section) => {
      const [start, end] = section.time_range;
      return currentTime >= start && currentTime <= end;
    }));

    if (foundSection) {
      console.log('현재 content는 ', foundSection.content);
      // console.log('현재 other은 ', foundSection.other);
      setCurrentSection(foundSection);

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

  useEffect(() => {
    if (audioPlaying) {
      foundCurrentContent();
    }
  }, [audioPlaying, currentTime]);

  return (
    <div className="Sub2">
      <div id = 'wrap'>
        <Logo />
        <Data radio_name = {radio_name} date = {date}/>
        {/* episode 컴포넌트로 구현하려고 했던 부분_s */}
        <div className="episode">
          <div id = "section1">
            <Section1
              content={currentSection.content}
              other={currentSection.other}
              youtubeStateCheck={youtubeStateCheck}
              />
          </div>
          <Section2 audioRef={audioRef} scriptData={scriptData} currentTime={currentTime} 
          currentSection={currentSection} setCurrentSection = {setCurrentSection} youtubeStateCheck={youtubeStateCheck}/>
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
          // onListen={handleAudioListen}  // 현재 재생 위치 감지
        ></ReactAudioPlayer>
      </div>
    </div>
  );
}

export default Sub2;
