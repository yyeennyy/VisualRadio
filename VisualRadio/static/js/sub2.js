window.onload = function() {
    getInfo().then(() => {
        getScript().then(() => startSubtitles());
        getWave();
        getImg();
    });
    const progress = document.querySelector('.progress');
    const progressBar = document.querySelector('.progress-bar')
    const currentTimeText = document.getElementById('currentTime');
    const durationText = document.getElementById('duration');
    
    audio.addEventListener('timeupdate', () => {
        const currentTime = audio.currentTime;
        const duration = audio.duration;
        const progress_time = currentTime / duration;
        progress.style.width = `${progress_time * 100}%`;
        const minutes = Math.floor(audio.currentTime / 60);
        const seconds = Math.floor(audio.currentTime % 60).toString().padStart(2, '0');
        currentTimeText.innerText = `${minutes}:${seconds}`;
    });
    
    audio.addEventListener('loadedmetadata', () => {
      const minutes = Math.floor(audio.duration / 60);
      const seconds = Math.floor(audio.duration % 60).toString().padStart(2, '0');
      durationText.innerText = `${minutes}:${seconds}`;
    });
    
    progressBar.addEventListener('click', (event) => {
      const barWidth = progressBar.clientWidth;
      const clickedPosition = event.clientX - progressBar.getBoundingClientRect().left;
      const newTime = (clickedPosition / barWidth) * audio.duration;
      audio.currentTime = newTime;
      progressBar.value = audio.duration;
    });
}

var broadcast = '';
var radio_name = '';
var date = '';
var subtitlesObj;
const audio = document.getElementById("audio");
const subtitleContainer = document.getElementById("subtitleContainer");
var subtitles = [];
let highlightedSubtitleIndex = -1;
const source = "http://localhost:5000"


function getInfo() {
    return fetch(`${source}/program_info`)
    .then((response) => response.json())
    .then((data) => 
        {
         broadcast = data.broadcast;
         radio_name = data.radio_name;
         date       = data.date;
         document.getElementById('info').innerHTML = `${radio_name}  ${date}`})
}

function getScript() {
    return fetch(`${source}/${broadcast}/${radio_name}/${date}/script`)
      .then((response) => response.json())
      .then((data) => {
        subtitlesObj = data;
        
        console.log(data);
        return data;
      });
}

function timeStringToFloat(time) {
    const [minutes, seconds] = time.split(':');
    const [secondsWithoutFraction] = seconds.split('.');
    const fraction = parseInt(seconds.split('.')[1]) || 0;
    const totalSeconds = parseInt(minutes) * 60 + parseInt(secondsWithoutFraction) + fraction / 1000;
    return parseFloat(totalSeconds.toFixed(3));
}

function startSubtitles() {
    const subtitlesWithTime = subtitlesObj.map(subtitle => ({
      txt: subtitle.txt,
      time: timeStringToFloat(subtitle.time)
    }));
  
    subtitlesWithTime.forEach(subtitle => {
      const block = document.createElement('div');
      block.innerText = subtitle.txt;
      block.addEventListener('click', () => {
        audio.currentTime = subtitle.time;
      });
      subtitleContainer.appendChild(block);
    });

    const containerHeight = subtitleContainer.getBoundingClientRect().height;
    const subtitleHeight = subtitleContainer.children[0].getBoundingClientRect().height;  
    audio.addEventListener('timeupdate', () => {
        const currentTime = audio.currentTime;
        for (let i = 0; i < subtitlesWithTime.length; i++) {
          const subtitle = subtitlesWithTime[i];
          const nextSubtitle = subtitlesWithTime[i + 1];
          if (nextSubtitle && nextSubtitle.time <= currentTime) {
            continue;
          }
          if (subtitle.time <= currentTime) {
            // 현재 재생 중인 자막을 강조합니다.
            subtitleContainer.children[i].style.fontWeight = 'bold';
            highlightedSubtitleIndex = i;
          } else {
            subtitleContainer.children[i].style.fontWeight = 'normal';
          }
        }
        // 나머지 자막들의 스타일을 일괄적으로 normal로 설정합니다.
        if (highlightedSubtitleIndex !== -1) {
          for (let i = 0; i < subtitlesWithTime.length; i++) {
            if (i !== highlightedSubtitleIndex) {
              subtitleContainer.children[i].style.fontWeight = 'normal';
            }
          }
        }
      
        // 강조 중인 자막이 항상 중앙에 오도록 스크롤 위치를 조정합니다.
        if (highlightedSubtitleIndex !== -1) {

            const highlightedSubtitle = subtitleContainer.children[highlightedSubtitleIndex];
            const containerTop = subtitleContainer.getBoundingClientRect().top;
            const highlightedSubtitleTop = highlightedSubtitle.getBoundingClientRect().top - containerTop;
            const subtitleHeight = highlightedSubtitle.getBoundingClientRect().height;
            const containerHeight = subtitleContainer.getBoundingClientRect().height;
            const scrollAmount = highlightedSubtitleTop - containerTop;
            subtitleContainer.scrollTo({
                top: subtitleContainer.scrollTop + scrollAmount+subtitleHeight*4,
                behavior: 'smooth',
            });
        }
      });
    }

function sleep(ms) {
    const wakeUpTime = Date.now() + ms;
    while (Date.now() < wakeUpTime) {}
}
  
function getWave() {
  fetch(`${source}/${broadcast}/${radio_name}/${date}/wave`)
    .then(response => response.blob())
    .then(data => {
      const audio = document.getElementById('audio');
      audio.src = URL.createObjectURL(data);
    })
    .catch(error => console.error(error));
}

function getImg() {
    console.log(broadcast, radio_name, date)
    fetch(`${source}/${broadcast}/${radio_name}/${date}/images`)
    .then(response => response.blob())
    .then(data => {
        document.getElementById('main_img').src = data.img_url
    })
}

const playPauseBtn = document.getElementById("play-pause-btn");

playPauseBtn.addEventListener("click", function() {
  if (audio.paused) {
    audio.play();
    playPauseBtn.innerHTML = '<i class="fa fa-pause"></i>';
    playPauseBtn.querySelector("img").src = "/static/images/pauseBtn.png";
    // playPauseBtn.innerText = "일시정지";
  } else {
    audio.pause();
    playPauseBtn.innerHTML = '<i class="fa fa-play"></i>';
    playPauseBtn.querySelector("img").src = "/static/images/playBtn.png";
    // playPauseBtn.innerText = "재생";
  }
});

const SCROLL_PAUSE_TIME = 200; // 일시 중지할 시간 (200ms)

const pauseSubtitleHighlighting = () => {
  audio.pause(); // audio 일시 정지
};

const resumeSubtitleHighlighting = () => {
  audio.play(); // audio 재생
};

// 스크롤 이벤트 리스너 등록
subtitleContainer.addEventListener('scroll', () => {
  pauseSubtitleHighlighting();
  // SCROLL_PAUSE_TIME(ms) 후 다시 자막 강조 재개
  setTimeout(resumeSubtitleHighlighting, SCROLL_PAUSE_TIME);
});

// // 검색 기능
// function findText() {
//   // 검색창에 입력한 text
//   let searchText = document.getElementById('searchBar').value;

//   if (searchText == null) {
//     alert("검색어를 입력해주세요.");
//   } else {
//     // 검색 결과 해당 text와 시간 저장
//     let matchedText = subtitlesObj.filter(subtitle => subtitle.txt.includes(searchText));
//     let matchedIndex = matchedText.map(subtitle => subtitlesObj.indexOf(subtitle));
//     let isStopping = false;

//     // 해당 시간으로 이동 > 엔터 누르면 다음 결과, 재생 버튼 누르면 break
//     if (matchedText.length != 0) {
//       for (let i = 0; i < matchedText.length; i++) {
//         audio.currentTime = matchedIndex[i];

//         if (window.event.keyCode == 13) {
//           continue;
//         }

//         document.getElementById("play-pause-btn").onclick = function () {
//           isStopping = true;
//         };

//         if (isStopping == true) {
//           break;
//         }
//       }

//     } else {
//       alert("검색 내용을 찾을 수 없습니다.");
//     }
//   }
// }

// 인덱스 선택
// 이런 흐름
// 버튼 클릭 시, 서버에서 시간대 받아서 그 시간부터 재생되게
// const part1 = document.getElementById('part1');
// const part2 = document.getElementById('part2');
// var time = '';

// function part1Play() {
//   return fetch(``) // 라디오 par1 시간
//   .then((response) => response.json())
//   .then((data) => 
//       {time = data;})
  
// }
// audio.currentTime = timeStringToFloat(time);



// 서버 확인해보기!!
