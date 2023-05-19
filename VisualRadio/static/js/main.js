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
  programElement.classList.add(radio_name);
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
    <div class="program_name" broadcast="${broadcast}" radio_name="${radio_name}">${radio_name}</div>
  `;
  return programElement;
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
getInfo();