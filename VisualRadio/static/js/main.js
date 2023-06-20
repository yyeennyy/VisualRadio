const channelsElement = document.getElementById("channels");

function createRadioBroadcast(broadcast) {
  const radioBroadcastElement = document.createElement("div");
  radioBroadcastElement.classList.add("radioBroadcast");
  radioBroadcastElement.innerHTML = `
    <div class="radioBroadcastName">${broadcast}</div>
  `;
  return radioBroadcastElement;
}

function createProgramElement(program, broadcast) {
  const { radio_name, img } = program;
  const programElement = document.createElement("div");
  programElement.classList.add("content");
  const radio_class = radio_name.replace(/\s/g, "")
  programElement.classList.add(radio_class);
  programElement.innerHTML = `
    <div class="cover_back">
      <div class="lp">
        <img class="imgControl" src="/static/images/lp.png">
      </div>
      <div class="cover">
        <img class="imgControl" src="${img}">
      </div>
      <div class="like">
        <img class="imgControl" src="/static/images/before_heart.png">
      </div>
    </div>
    <div class="program_name" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
  `;
  return programElement;
}

function setLikeImage(programElement, broadcast, radio_name) {
  const likeElement = programElement.querySelector(".like");
  const heartImage = likeElement.querySelector(".imgControl");

  const cookieValue = getCookie(broadcast, radio_name);
  if (cookieValue === "true") {
    heartImage.src = '/static/images/heart.png';
  } else {
    heartImage.src = '/static/images/before_heart.png';
  }
}

function getInfo() {
  return fetch("/radio")
    .then((response) => response.json())
    .then((data) => {
      data.forEach(({ broadcast, programs }) => {
        const radioBroadcastElement = createRadioBroadcast(broadcast);
        programs.forEach((program) => {
          const programElement = createProgramElement(program, broadcast);
          radioBroadcastElement.appendChild(programElement);

          // 클릭 이벤트 추가
          programElement.addEventListener("click", function (event) {
            const clickDiv = event.currentTarget;
            const radio_name = clickDiv.querySelector(".program_name").getAttribute("radio_name");
            const broadcast = clickDiv.querySelector(".program_name").getAttribute("broadcast");
            window.location.href = "/subpage?broadcast=" + broadcast + "&radio_name=" + radio_name;
          });

          // "like" 요소에 이벤트 리스너 추가
          const likeElement = programElement.querySelector(".like");
          const heartImage = likeElement.querySelector(".imgControl");
          likeElement.addEventListener("click", function (event) {
            event.stopPropagation(); // 이벤트 전파 중지 => 이거 안하면 부모 요소의 클릭 이벤트가 적용되어 버튼 클릭시 sub1 페이지로 이동됨

            if (heartImage.src.includes('before_heart.png')) {
              heartImage.src = '/static/images/heart.png';

              const radio_name = programElement.querySelector(".program_name").getAttribute("radio_name");
              const broadcast = programElement.querySelector(".program_name").getAttribute("broadcast");
              const url = `/like/${broadcast}/${radio_name}`;
              
              // 쿠키 생성
              setCookie(broadcast, radio_name, "true", 7);
              const cookieValue = getCookie(broadcast, radio_name);
              console.log(cookieValue);
              
              fetch(url)
                .then(response => {
                  if (!response.ok) {
                    throw new Error("실패ㅠㅠ");
                  }
                  // 성공적으로 요청을 보낸 후의 처리
                  console.log("성공!!!");
                })
                .catch(error => {
                  console.error('Error:', error);
                });
            } else {
              heartImage.src = '/static/images/before_heart.png';

              const radio_name = programElement.querySelector(".program_name").getAttribute("radio_name");
              const broadcast = programElement.querySelector(".program_name").getAttribute("broadcast");
              const unlikeUrl = `/unlike/${broadcast}/${radio_name}`;

              // 쿠키 생성
              setCookie(broadcast, radio_name, "false", 7);
              const cookieValue = getCookie(broadcast, radio_name);
              console.log(cookieValue);

              fetch(unlikeUrl)
                .then(response => {
                  if (!response.ok) {
                    throw new Error("실패ㅠㅠ");
                  }
                  // 성공적으로 요청을 보낸 후의 처리
                  console.log("성공!!!");
                })
                .catch(error => {
                  console.error('Error:', error);
                });
            }
          });
          // 쿠키 값에 따라 좋아요 이미지 설정
          const radio_name = programElement.querySelector(".program_name").getAttribute("radio_name");
          setLikeImage(programElement, broadcast, radio_name);
        });
        channelsElement.appendChild(radioBroadcastElement);
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
}
//     return fetch(`/radio`)
//     .then((response) => response.json())
//     .then((data) => 
//         {
//             console.log(data);
//             // 이 부분 아직 mbc만 초점을 맞춰서 구성되어 있음! 나중에는 들어온 데이터별로 방송사를 다르게
//             // 설정할 수 있도록 고쳐야함.
//             for(let i=0; i<data.length; i++){
//                 mbcElements[i].broadcast =  data[i].broadcast;
//                 mbcElements[i].innerHTML = `<img class="imgControl mbcFm4u_img" src = "${data[i].radio_img_url}" > ${data[i].radio_name}`;
//                 mbcElements[i].radio_name =  data[i].radio_name;

//                 mbcElements[i].addEventListener('click' , function(event){
//                     let clickDiv = event.currentTarget;
//                     let radio_name = clickDiv.radio_name;
//                     let broadcast = clickDiv.broadcast;
//                     window.location.href = '/subpage?broadcast=' + broadcast + '&radio_name=' + radio_name;
                    
//                     // fetch(`/${broadcast}/${radio_name}/subpage`)
//                     //     .then((response) => response.json())
//                     //     .then((data) => {
//                     //         location.href = data.url;
//                     // }
//                 ;})
//             }
//         });
// }

getInfo()

const goPro = document.getElementById('goPrograms')
const goAdm = document.getElementById('goAdmin')

goPro.addEventListener("click", function (event) {
  const clickDiv = event.currentTarget;
  window.location.href = "/programs";
});
goAdm.addEventListener("click", function (event) {
  const clickDiv = event.currentTarget;
  window.location.href = "/admin";
});