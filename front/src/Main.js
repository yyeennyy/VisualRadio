import React from "react";
import "./Main.css";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
// import "./js/Main.js";

const Main = () => {
  const navigate = useNavigate();

  const goToSUb = () => {
    console.log("he");
    navigate("/subpage");
  };
  const goToAdmin = () => {
    console.log("he");
    navigate("/admin");
  };

  console.log("[로그로그]")

  useEffect(() => {
    // var urlParams = new URLSearchParams(window.location.search);
    // var broadcast = urlParams.get("broadcast");
    // var radio_name = urlParams.get("radio_name");
    // let broadcast = "MBC FM4U"
    // let radio_name = "이석훈의 브런치카페"
    // getCookie(broadcast, radio_name);
    // setLikeImage(broadcast, radio_name);

    // if (broadcast !== null && radio_name !== null) {
    //   broadcast = broadcast.replace(/\/$/, "");
    //   getCookie(broadcast, radio_name);
    //   setLikeImage(broadcast, radio_name);
    // }

    const channelsElement = document.querySelector("#channels");
    // console.log(channelsElement)

    function createRadioBroadcast(broadcast) {
      const radioBroadcastElement = document.createElement("div");
      //   radioBroadcastElement.classList.add("radioBroadcast");
      radioBroadcastElement.setAttribute("className", "radioBroadcast");
      radioBroadcastElement.innerHTML = `
          <div className="radioBroadcastName">${broadcast}</div>
        `;
      return radioBroadcastElement;
    }

    function createProgramElement(program, broadcast) {
      const { radio_name, img } = program;
      const programElement = document.createElement("div");
      //   programElement.classList.add("content");

      const radio_class = radio_name.replace(/\s/g, "");
      //   programElement.classList.add(radio_class);
      // programElement.setAttribute("className", `content ${radio_class}`);
      programElement.setAttribute("className", `content`);
      programElement.addEventListener("onClick", goToSUb);
      programElement.innerHTML = `
            <div className="cover_back">
                <div className="lp">
                    <img className="imgControl" src="/static/images/lp.png">
                </div>
                <div className="cover">
                    <img className="imgControl" src="${img}">
                </div>
                <div className="like">
                    <img className="imgControl" src="/static/images/before_heart.png">
                </div>
            </div>
            <div className="program_name" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
        `;
      return programElement;
    }

    function setLikeImage(programElement, broadcast, radio_name) {
      // console.log(document.querySelector(".App"))
      // console.log(
      //   document.querySelector("[class = 'cover_back']")
      //   )
      // const programElement = document.querySelector(
      //   `.program_name[broadcast="${broadcast}"][radio_name="${radio_name}"]`
      // );
      // console.log(11)
      // console.log(programElement)
      // if (programElement) {
      const likeElement = programElement.querySelector("[className = 'like']");
      // console.log(likeElement)
      // .querySelector(".like");
      const heartImage = likeElement.querySelector(
        "[className = 'imgControl']"
      );

      const cookieValue = getCookie(broadcast, radio_name);
      if (cookieValue === "true") {
        heartImage.src = "/static/images/heart.png";
      } else {
        heartImage.src = "/static/images/before_heart.png";
      }
      // }
    }

    function getInfo() {
      console.log("[tmp] getInfo() 요청함");
      return fetch("/api/radio")
        .then((response) => response.json())
        .then((data) => {
          data.forEach(({ broadcast, programs }) => {
            const radioBroadcastElement = createRadioBroadcast(broadcast);
            programs.forEach((program) => {
              console.log(`[tmp] ${broadcast}`);
              const programElement = createProgramElement(program, broadcast);
              radioBroadcastElement.appendChild(programElement);

              // 클릭 이벤트 추가
              programElement.addEventListener("click", function (event) {
                const clickDiv = event.currentTarget;
                const radio_name = clickDiv
                  .querySelector("[className = 'program_name']")
                  .getAttribute("radio_name");
                const broadcast = clickDiv
                  .querySelector("[className = 'program_name']")
                  .getAttribute("broadcast");
                window.location.href =
                  "/subpage?broadcast=" +
                  broadcast +
                  "&radio_name=" +
                  radio_name;
              });

              // "like" 요소에 이벤트 리스너 추가
              //   const likeElement = programElement.querySelector('[className = "like"]');
              const likeElement = programElement.querySelector(
                '[className = "like"]'
              );
              //   const likeElement1 = programElement.querySelector(".like");
              // console.log(likeElement)
              //   console.log(likeElement1)
              const heartImage = likeElement.querySelector(
                "[className = 'imgControl']"
              );
              likeElement.addEventListener("click", function (event) {
                event.stopPropagation(); // 이벤트 전파 중지 => 이거 안하면 부모 요소의 클릭 이벤트가 적용되어 버튼 클릭시 sub1 페이지로 이동됨

                if (heartImage.src.includes("before_heart.png")) {
                  heartImage.src = "/static/images/heart.png";

                  const radio_name = programElement
                    .querySelector("[className = 'program_name']")
                    .getAttribute("radio_name");
                  const broadcast = programElement
                    .querySelector("[className = 'program_name']")
                    .getAttribute("broadcast");
                  const url = `/like/${broadcast}/${radio_name}`;
                  // 쿠키 생성
                  setCookie(broadcast, radio_name, "true", 365);
                  const cookieValue = getCookie(broadcast, radio_name);
                  // console.log(cookieValue);

                  fetch(url)
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error("실패ㅠㅠ");
                      }
                      // 성공적으로 요청을 보낸 후의 처리
                      console.log("성공!!!");
                    })
                    .catch((error) => {
                      console.error("Error:", error);
                    });
                } else {
                  heartImage.src = "/static/images/before_heart.png";

                  const radio_name = programElement
                    .querySelector("[className = 'program_name']")
                    .getAttribute("radio_name");
                  const broadcast = programElement
                    .querySelector("[className = 'program_name']")
                    .getAttribute("broadcast");
                  const unlikeUrl = `/unlike/${broadcast}/${radio_name}`;

                  // 쿠키 생성
                  setCookie(broadcast, radio_name, "false", 365);
                  const cookieValue = getCookie(broadcast, radio_name);
                  console.log(cookieValue);

                  fetch(unlikeUrl)
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error("실패ㅠㅠ");
                      }
                      // 성공적으로 요청을 보낸 후의 처리
                      console.log("성공!!!");
                    })
                    .catch((error) => {
                      console.error("Error:", error);
                    });
                }
              });
              // 쿠키 값에 따라 좋아요 이미지 설정
              const radio_name = programElement
                .querySelector("[className = 'program_name']")
                .getAttribute("radio_name");
              // console.log(2)
              setLikeImage(programElement, broadcast, radio_name);
            });
            channelsElement.appendChild(radioBroadcastElement);
          });
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
    console.log("[tmp] window 로드됨 - getInfo() 요청해야함");
    getInfo();

    // const goPro = document.querySelector("#goPrograms");
    const goAdm = document.getElementById("goAdmin");

    // console.log(goPro);
    // goPro.addEventListener("click", function (event) {
    //   window.location.href = "/programs";
    // });

    goAdm.addEventListener("click", function (event) {
      window.location.href = "/admin";
    });

    function setCookie(broadcast, radio_name, value, days) {
      const cookieName = `${broadcast}_${radio_name}`;
      const expirationDate = new Date();
      expirationDate.setDate(expirationDate.getDate() + days);
      const cookieValue = `${value}; expires=${expirationDate.toUTCString()}`;
      document.cookie = `${cookieName}=${cookieValue}`;
    }

    function getCookie(broadcast, radio_name) {
      const cookieName = `${broadcast}_${radio_name}`;
      const cookieValue = document.cookie
        .split("; ")
        .find((cookie) => cookie.startsWith(`${cookieName}=`));

      if (cookieValue) {
        const value = cookieValue.split("=")[1];
        return value;
      }

      return null;
    }
  });

  return (
    <>
      <div id="wrap">
        <div id="header">
          <a href="/">
            <div id="logo">
              <img id="logoImg" src="/static/images/logo.png" />
            </div>
          </a>
        </div>
        <div id="searchOptionBox">
          <form id="searchForm">
            <input
              type="text"
              id="searchInput"
              placeholder="| 흘러간 소리를 검색해보세요!"
              size="120"
            />
            <button type="submit" id="searchButton">
              검색
            </button>
          </form>
        </div>
        <div id="searchMenu">
          <ul>
            <li id="search">통합검색</li>
            <li id="program">프로그램</li>
            <li id="user">청취자</li>
            <li id="contents">컨텐츠</li>
          </ul>
        </div>
        <div id="resultTextTitle"></div>
        <div id="resultContainer">
          <div id="result">
            <div className="resultBox">
              <div className="resultTitle">프로그램</div>
              <p id="a"></p>
              <div id="resultPrograms"></div>
            </div>
            <hr id="h" />
            <div className="resultBox">
              <div className="resultTitle">청취자</div>
              <p id="b"></p>
              <div className="resultUsers"></div>
            </div>
            <hr id="r" />
            <div className="resultBox">
              <div className="resultTitle">컨텐츠</div>
              <p id="c"></p>
              <div className="resultContents"></div>
            </div>
          </div>
        </div>
      </div>
      <div id="channels"></div>
      <div id="goAdmin" onClick={goToAdmin}>
        goAdmin!!!
      </div>
      {/* <div id='goPrograms'>goPrograms!!</div> */}
    </>
  );
};

export default Main;
