let broadcast
let radio_name
let date

window.onload = function() {
  const urlParams = new URLSearchParams(window.location.search);
  broadcast = urlParams.get('broadcast');
  radio_name = urlParams.get('radio_name');
  date = urlParams.get('date');
  document.getElementById('info').innerHTML = `${radio_name}  ${date}`
  getContents()
  getScript(broadcast, radio_name, date).then(() => startSubtitles());
  get_listeners();
  getWave(broadcast, radio_name, date);
  getImg(broadcast, radio_name, date).then(() => {
    startImageChecking();
  })
  startSectionChecking()
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
    showImageAtCurrentTime();
  });
}
var subtitlesObj;
const audio = document.getElementById("audio");
const subtitleContainer = document.getElementById("subtitleContainer");
var subtitles = [];
let highlightedSubtitleIndex = -1;


function getScript(broadcast, radio_name, date) {
    return fetch(`/${broadcast}/${radio_name}/${date}/script`)
      .then((response) => response.json())
      .then((data) => {
        subtitlesObj = data;
        
        // console.log(data);
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

let subtitlesWithTime;

function startSubtitles() {
  subtitlesWithTime = subtitlesObj.map(subtitle => ({
    txt: subtitle.txt,
    time: timeStringToFloat(subtitle.time)
  }));

  subtitlesWithTime.forEach(subtitle => {
    const block = document.createElement('div');
    block.innerText = subtitle.txt;
    block.addEventListener('click', () => {
      audio.currentTime = subtitle.time;
      showImageAtCurrentTime();
    });
    subtitleContainer.appendChild(block);
  });
  }

function hilightSubtitle(){
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
          top: subtitleContainer.scrollTop + scrollAmount+subtitleHeight,
          behavior: 'smooth',
      });
  }
}
audio.addEventListener('timeupdate', hilightSubtitle);


function sleep(ms) {
    const wakeUpTime = Date.now() + ms;
    while (Date.now() < wakeUpTime) {}
}
  
const loading = document.getElementById('loading');

function getWave(broadcast, radio_name, date) {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', `/${broadcast}/${radio_name}/${date}/wave`, true);
  xhr.responseType = 'blob';
  xhr.onprogress = function(event) {
    if (event.lengthComputable) {
      const percentComplete = (event.loaded / event.total) * 100;
      console.log(`Loading... ${percentComplete.toFixed(2)}%`);
    } else {
      console.log('Loading...');
    }
  };
  xhr.onload = function(event) {
    loading.innerHTML = '/';
    const blob = xhr.response;
    const audioURL = URL.createObjectURL(blob); // Blob 객체를 URL로 변환
    document.getElementById('audio').src = audioURL; // audio 엘리먼트에 URL 할당
  };
  xhr.send();
}

function parseTime(timeString) {
  const [min, secMillisec] = timeString.split(':');
  const [sec, millisec] = secMillisec.split('.');
  return (+min * 60 + +sec) * 1000 + +millisec;
}

let audioCurrentTime = 0;

audio.addEventListener('timeupdate', () => {
  audioCurrentTime = audio.currentTime;
});

let currentIndex=0;
const mainImg = document.getElementById('main_img');
var data = [];

function getImg(broadcast, radio_name, date) {
  return fetch(`/${broadcast}/${radio_name}/${date}/images`)
    .then(response => response.json())
    .then(imgUrl => {
        data = imgUrl;
})}

function showImg(){
      // console.log(`showImg idex : ${currentIndex}`)
      var { img_url, time } = data[currentIndex];
      var nextImgTime;

      // preload the next image
      if (currentIndex < data.length - 1) {
        const nextImg = new Image();
        const nextImgUrl = `${data[currentIndex + 1].img_url}`;
        nextImgTime = parseTime(data[currentIndex + 1].time) / 1000;
        nextImg.src = nextImgUrl;
      }

      // display the current image
      mainImg.src = img_url;
      const timeDiff = Math.abs(audioCurrentTime - nextImgTime);
      // console.log(timeDiff);

      // check if it's time to switch to the next image
      // if (timeDiff < 0.1 && timeDiff > 0) {
      if (timeDiff > 0 && timeDiff < 0.08) {
        currentIndex = (currentIndex + 1) % data.length;
        const nextImgUrl = `${data[currentIndex].img_url}`;
        // preload the image after the next image
        if (currentIndex < data.length - 1) {
          const nextNextImg = new Image();
          const nextNextImgUrl = `${data[currentIndex + 1].img_url}`;
          nextNextImg.src = nextNextImgUrl;
        }
        mainImg.src = nextImgUrl;
      }

    }

function preload(url) {
  const img = new Image();
  img.src = url;
}

function startImageChecking() {
  setInterval(() => {
      showImg();
      // showContents();
    }, 1);
  }


function showImageAtCurrentTime() {
  fetch(`/${broadcast}/${radio_name}/${date}/images`)
    .then(response => response.json())
    .then(data => {
      const audioCurrentTime = audio.currentTime;
      let closestTimeDiff = Number.MAX_SAFE_INTEGER;
      let closestImgUrl = '';
      let i = -1;
      let closetIndex;
      data.forEach(({ img_url, time }) => {
        i++;
        const timeInMillisec = time ? parseTime(time) : 0;
        const imgTime = timeInMillisec / 1000;
        const timeDiff = Math.abs(audioCurrentTime - imgTime);

        if (timeDiff < closestTimeDiff && imgTime < audioCurrentTime) {
          closetIndex = i;
          closestTimeDiff = timeDiff;
          closestImgUrl = img_url;
        }
      });

      mainImg.src = closestImgUrl;
      currentIndex = closetIndex;
      startImageChecking();
    })
    .catch(error => {
      // console.error('Error fetching image:', error);
    });
}

const playPausediv = document.getElementById("play-pause-btn");

playPausediv.addEventListener("click", function() {
  if (audio.paused) {
    audio.play();
    playPausediv.innerHTML = '<img class="btn" src = "/static/images/pauseBtn.png" ><i class="fa fa-pause"></i>';
  } else {
    audio.pause();
    playPausediv.innerHTML = '<img class="btn" src = "/static/images/playBtn.png" ><i class="fa fa-play"></i>';
  }
});

// showContents()

function startSectionChecking() {
  setInterval(() => {
      // showImg();
      showContents();
    }, 1000);
  }

// var contents = [];


let contents;

function getContents() {
  return fetch(`/${broadcast}/${radio_name}/${date}/section`)
    .then(response => response.json())
    .then(imgUrl => {
      contents = imgUrl;
      return imgUrl;
    });
}


function showContents(){
    const audioCurrentTime = audio.currentTime;
    console.log(contents)
    
    for (const item of contents) {
      if (item.type === 1 || item.type === 2) {
        // console.log(11111111)
        const startTime = timeStringToFloat(item.start_time);
        const endTime = timeStringToFloat(item.end_time);
        // console.log(startTime)
        // console.log(audioCurrentTime)
        if ((audioCurrentTime >= startTime && audioCurrentTime <= endTime) & timeStringToFloat("0:00.000") != audio.currentTime) {
          // console.log(11111111112222222222)
          if (item.type == 1) displayImage('/static/images/ading.png');
          else displayImage();
          return;
        }
      }
  }
  removeImage();
    }

function displayImage(imageUrl){
    // 이미지를 화면에 표시하는 함수
    const imageElement = document.getElementById('episode');
    const imageSection = document.getElementById('section1');
    const titleSection = document.getElementById('section2');
    imageElement.setAttribute('src', imageUrl)
    imageSection.style.display = 'none';
    titleSection.style.display = 'none';
}

function removeImage() {
  // 이미지를 제거하는 함수
  const imageElement = document.getElementById('episode');
  const imageSection = document.getElementById('section1');
  const titleSection = document.getElementById('section2');

  if (imageElement) {
    imageElement.removeAttribute('src'); // 이미지 요소의 src 속성 제거
    imageSection.style.display = 'block';
    titleSection.style.display = 'block';
  }
}


// let isScrolling = false;

// subtitleContainer.addEventListener('scroll', () => {
//   if (isScrolling) {
//     // 일시적으로 timeupdate 이벤트 처리 중지
//     audio.removeEventListener('timeupdate', hilightSubtitle);
//     clearTimeout(timeoutId);
//   }
//   isScrolling = true;

//   // 1.5초 후에 timeupdate 이벤트 처리 재개
//   const timeoutId = setTimeout(() => {
//     isScrolling = false;
//     audio.addEventListener('timeupdate', hilightSubtitle);
//   }, 100);
// });


function get_listeners(){
  let url = `/${broadcast}/${radio_name}/${date}/listeners`;

  fetch(url)
  .then(response => response.json())
  .then(data => {
    const parsedData = JSON.parse(data);
    if (parsedData[0]['code']==''){
      return
    } else {
      var textAboveListener = document.getElementById("textAboveListener");
      var listenerBox = document.getElementById("listenerBox");
      listenerBox.style.visibility = "visible";
      textAboveListener.style.visibility = "visible";
      console.log('바꿈')
      parsedData.forEach(listener => {
        const code = listener['code'];
        const keys = listener['keyword'];
        const time = listener['time'];
        const listenerLine = document.createElement("div");
        listenerLine.id = "listenerLine"
        listenerLine.classList.add("hover-zoom", "hover-zoom:hover");
        listenerLine.textContent = code + "님: " + keys;
        listenerBox.appendChild(listenerLine);

        // 클릭 리스너 등록
        listenerLine.addEventListener("click", function() {
          audio.currentTime = timeStringToFloat(time);
          showImageAtCurrentTime();
        });
      });
    }
  })
  .catch(error => {
    console.log("Error fetching JSON data:", error);
  });

}