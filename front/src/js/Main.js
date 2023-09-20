// window.onload = function () {
//   var urlParams = new URLSearchParams(window.location.search);
//   var broadcast = urlParams.get("broadcast");
//   var radio_name = urlParams.get("radio_name");
//   getCookie(broadcast, radio_name);
//   setLikeImage(broadcast, radio_name);

//   if (broadcast !== null && radio_name !== null) {
//     broadcast = broadcast.replace(/\/$/, "");
//     getCookie(broadcast, radio_name);
//     setLikeImage(broadcast, radio_name);
//   }

//   const channelsElement = document.getElementById("channels");
//   console.log(channelsElement)

//   function createRadioBroadcast(broadcast) {
//     const radioBroadcastElement = document.createElement("div");
//     radioBroadcastElement.classList.add("radioBroadcast");
//     radioBroadcastElement.innerHTML = `
//     <div className="radioBroadcastName">${broadcast}</div>
//   `;
//     return radioBroadcastElement;
//   }

//   function createProgramElement(program, broadcast) {
//     const { radio_name, img } = program;
//     const programElement = document.createElement("div");
//     programElement.classList.add("content");
//     const radio_class = radio_name.replace(/\s/g, "");
//     programElement.classList.add(radio_class);
//     programElement.innerHTML = `
//     <div className="cover_back">
//       <div className="lp">
//         <img className="imgControl" src="/static/images/lp.png">
//       </div>
//       <div className="cover">
//         <img className="imgControl" src="${img}">
//       </div>
//       <div className="like">
//         <img className="imgControl" src="/static/images/before_heart.png">
//       </div>
//     </div>
//     <div className="program_name" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
//   `;
//     return programElement;
//   }

//   function setLikeImage(broadcast, radio_name) {
//     const programElement = document.querySelector(
//       `.program_name[broadcast="${broadcast}"][radio_name="${radio_name}"]`
//     );

//     if (programElement) {
//       const likeElement = programElement
//         .closest(".content")
//         .querySelector(".like");
//       const heartImage = likeElement.querySelector(".imgControl");

//       const cookieValue = getCookie(broadcast, radio_name);
//       if (cookieValue === "true") {
//         heartImage.src = "/static/images/heart.png";
//       } else {
//         heartImage.src = "/static/images/before_heart.png";
//       }
//     }
//   }

//   function getInfo() {
//     return fetch("./radio.json")
//       .then((response) => response.json())
//       .then((data) => {
//         console.log(data)
//         data.forEach(({ broadcast, programs }) => {
//           const radioBroadcastElement = createRadioBroadcast(broadcast);
//           programs.forEach((program) => {
//             const programElement = createProgramElement(program, broadcast);
//             console.log(programElement);
//             radioBroadcastElement.appendChild(programElement);

//             // 클릭 이벤트 추가
//             programElement.addEventListener("click", function (event) {
//               const clickDiv = event.currentTarget;
//               const radio_name = clickDiv.querySelector(".program_name").getAttribute("radio_name");
//               const broadcast = clickDiv.querySelector(".program_name").getAttribute("broadcast");
//               window.location.href = "/subpage?broadcast=" + broadcast + "&radio_name=" + radio_name;
//             });

//             // "like" 요소에 이벤트 리스너 추가
//             const likeElement = programElement.querySelector(".like");
//             console.log(likeElement)
//             const heartImage = likeElement.querySelector(".imgControl");
//             likeElement.addEventListener("click", function (event) {
//               event.stopPropagation(); // 이벤트 전파 중지 => 이거 안하면 부모 요소의 클릭 이벤트가 적용되어 버튼 클릭시 sub1 페이지로 이동됨

//               if (heartImage.src.includes("before_heart.png")) {
//                 heartImage.src = "/static/images/heart.png";

//                 const radio_name = programElement
//                   .querySelector(".program_name")
//                   .getAttribute("radio_name");
//                 const broadcast = programElement
//                   .querySelector(".program_name")
//                   .getAttribute("broadcast");
//                 const url = `/like/${broadcast}/${radio_name}`;

//                 // 쿠키 생성
//                 setCookie(broadcast, radio_name, "true", 365);
//                 const cookieValue = getCookie(broadcast, radio_name);
//                 console.log(cookieValue);

//                 fetch(url)
//                   .then((response) => {
//                     if (!response.ok) {
//                       throw new Error("실패ㅠㅠ");
//                     }
//                     // 성공적으로 요청을 보낸 후의 처리
//                     console.log("성공!!!");
//                   })
//                   .catch((error) => {
//                     console.error("Error:", error);
//                   });
//               } else {
//                 heartImage.src = "/static/images/before_heart.png";

//                 const radio_name = programElement
//                   .querySelector(".program_name")
//                   .getAttribute("radio_name");
//                 const broadcast = programElement
//                   .querySelector(".program_name")
//                   .getAttribute("broadcast");
//                 const unlikeUrl = `/unlike/${broadcast}/${radio_name}`;

//                 // 쿠키 생성
//                 setCookie(broadcast, radio_name, "false", 365);
//                 const cookieValue = getCookie(broadcast, radio_name);
//                 console.log(cookieValue);

//                 fetch(unlikeUrl)
//                   .then((response) => {
//                     if (!response.ok) {
//                       throw new Error("실패ㅠㅠ");
//                     }
//                     // 성공적으로 요청을 보낸 후의 처리
//                     console.log("성공!!!");
//                   })
//                   .catch((error) => {
//                     console.error("Error:", error);
//                   });
//               }
//             });
//             // 쿠키 값에 따라 좋아요 이미지 설정
//             const radio_name = programElement
//               .querySelector(".program_name")
//               .getAttribute("radio_name");
//             setLikeImage(programElement, broadcast, radio_name);
//           });
//           channelsElement.appendChild(radioBroadcastElement);
//         });
//       })
//       .catch((error) => {
//         console.error("Error:", error);
//       });
//   }

//   getInfo();

//   const goPro = document.getElementById("goPrograms");
//   const goAdm = document.getElementById("goAdmin");

//   console.log(goPro);
//   goPro.addEventListener("click", function (event) {
//     window.location.href = "/programs";
//   });
//   goAdm.addEventListener("click", function (event) {
//     window.location.href = "/admin";
//   });

//   function setCookie(broadcast, radio_name, value, days) {
//     const cookieName = `${broadcast}_${radio_name}`;
//     const expirationDate = new Date();
//     expirationDate.setDate(expirationDate.getDate() + days);
//     const cookieValue = `${value}; expires=${expirationDate.toUTCString()}`;
//     document.cookie = `${cookieName}=${cookieValue}`;
//   }

//   function getCookie(broadcast, radio_name) {
//     const cookieName = `${broadcast}_${radio_name}`;
//     const cookieValue = document.cookie
//       .split("; ")
//       .find((cookie) => cookie.startsWith(`${cookieName}=`));

//     if (cookieValue) {
//       const value = cookieValue.split("=")[1];
//       return value;
//     }

//     return null;
//   }
// };
