import React from "react";
import { useState } from "react";
import "./Sub1.css";
import { useNavigate } from "react-router-dom";

const Sub1 = () => {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);

  const navigate = useNavigate();
    
  const goToContent = () => {
      navigate("/contents");
    }

  // const handlePrevCalClick = () => {
  //   // 클릭 시 calMonth 값을 1 감소시킴
  //   if(month == 0){
  //     setMonth(12)
  //     setYear(year-1)
  //   }
  //   setMonth(month - 1);

  // }

  //   const handleNextCalClick = () => {
  //     // 클릭 시 calMonth 값을 1 증가시킴
  //     if(month == 13){
  //       setMonth(1);
  //       setYear(year+1);
  //     }
  //     setMonth(month + 1);

  //   };

  const handlePrevCalClick = () => {
    // 클릭 시 calMonth 값을 1 감소시킴
    setMonth(month - 1);
  };

  const handleNextCalClick = () => {
    // 클릭 시 calMonth 값을 1 증가시킴
    setMonth(month + 1);
  };

  window.onload = () => {
    
    let urlParams = new URLSearchParams(window.location.search);
    let broadcast = urlParams.get('broadcast').replace(/\/$/, '');
    let radio_name = urlParams.get('radio_name');
    // let broadcast = "MBC FM4U";
    // let radio_name = "이석훈의브런치카페";
    let prevCal = document.getElementById("prevCal");
    let nextCal = document.getElementById("nextCal");
    let radio_img = document.getElementById("radioImg");
    console.log(radio_img);
    let radio_info = document.getElementById("radioInfo");
    const heartImg = document.getElementById("imgControl");
    let today = new Date(); // 페이지를 로드한 날짜를 저장
    today.setHours(0, 0, 0, 0); // 비교 편의를 위해 today의 시간을 초기화
  
    let nowMonth = new Date(); // 현재 달을 페이지를 로드한 날의 달로 초기화
  
    console.log(radio_name, broadcast);
    buildCalendar(broadcast, radio_name);
    showImg(broadcast, radio_name);
    showInfo(radio_name);
    showLikeCnt(broadcast, radio_name);
    getCookie(broadcast, radio_name);
    setLikeImage(broadcast, radio_name);
    // checkCookie(broadcast, radio_name);
    // 웹 페이지가 로드되면 buildCalendar 실행
  
    // 달력 생성 : 해당 달에 맞춰 테이블을 만들고, 날짜를 채워 넣음
    function buildCalendar(broadcast, radio_name) {
      let month = nowMonth.getMonth() + 1; // getMonth()는 0부터 시작하므로 1을 더해서 실제 월 값을 얻습니다.
      console.log("현재 월" + nowMonth);
      console.log("월 파라미터" + month);

      let firstDate = new Date(nowMonth.getFullYear(), nowMonth.getMonth(), 1); // 이번달 1일
      let lastDate = new Date(nowMonth.getFullYear(), nowMonth.getMonth() + 1, 0); // 이번달 마지막날
  
      // 12월 달력 구현이 안되는 것이 날짜 계산 때문일까? 했는데 아님 => 이렇게 안해도 마지막날 계산 잘 됨
      // let lastDate;
  
      // if (nowMonth.getMonth() === 11) {
      //     lastDate = new Date(nowMonth.getFullYear() + 1, 0, 0); // 다음 해 1월 첫째날의 전일로 설정
      // } else {
      //     lastDate = new Date(nowMonth.getFullYear(), nowMonth.getMonth() + 1, 0); // 이번달 마지막날
      // }
  
      document.querySelector("#calYear").innerText = nowMonth.getFullYear();             // 연도 숫자 갱신
      document.querySelector("#calMonth").innerText = leftPad(nowMonth.getMonth() + 1);  // 월 숫자 갱신
      // calYear.innerText = nowMonth.getFullYear();             // 연도 숫자 갱신
      // calMonth.innerText = leftPad(nowMonth.getMonth() + 1);  // 월 숫자 갱신
  
      // let tbody_Calendar = document.querySelector("[className = 'calendar'] tbody");
      let tbody_Calendar = document.querySelector(".calendar tbody");
      console.log(tbody_Calendar);
      while (tbody_Calendar.rows.length > 0) {                        // 이전 출력 결과가 남아있는 경우 초기화
          tbody_Calendar.deleteRow(tbody_Calendar.rows.length - 1);
      }
  
      let nowRow = tbody_Calendar.insertRow(); // 첫번째 행 추가
  
      for (let j = 0; j < firstDate.getDay(); j++) {
        // 이번달 1일의 요일만큼
        let nowColumn = nowRow.insertCell(); // 열 추가
      }
  
      fetchData(radio_name, year, month).then((data) => {
        let dateOk = JSON.parse(data);
        // console.log(data);
        // let dateOk = data;
        for (
          let nowDay = firstDate;
          nowDay <= lastDate;
          nowDay.setDate(nowDay.getDate() + 1)
        ) {
          // day는 날짜를 저장하는 변수, 이번달 마지막날까지 증가시키며 반복
          console.log(nowDay);
          let nowColumn = nowRow.insertCell(); // 새 열을 추가하고
          nowColumn.innerText = leftPad(nowDay.getDate()); // 추가한 열에 날짜 입력
          nowColumn.setAttribute(
            "date",
            year + "-" + leftPad(month) + "-" + leftPad(nowDay.getDate())
          );
          let date = nowDay.getDate();
          // console.log(dateOk[0])
          for (let i = 0; i < dateOk.length; i++) {
            // console.log(dateOk[0])
            // console.log(dateOk[i].date)
            if (dateOk[i].date == date) {
              console.log("match!!")
              nowColumn.setAttribute("className", "day")
              // nowColumn.className = "day";
              // nowColumn.setAttribute("style", `{{ backgroundImage: "url(${background})" }}`)
              nowColumn.addEventListener("onClick", goToContent);
              nowColumn.addEventListener("click", function (event) {
                let clickDiv = event.currentTarget;
                let click_date = clickDiv.getAttribute("date");
                window.location.href =
                  "/contents?broadcast=" +
                  broadcast +
                  "&radio_name=" +
                  radio_name +
                  "&date=" +
                  click_date;
              });
            }
          }
  
          if (nowDay.getDay() == 0) {
            // 일요일인 경우 글자색 빨강으로
            nowColumn.style.color = "#DC143C";
          }
          if (nowDay.getDay() == 6) {
            // 토요일인 경우 글자색 파랑으로 하고
            nowColumn.style.color = "#0000CD";
            nowRow = tbody_Calendar.insertRow(); // 새로운 행 추가
          }
        }
      });
    }
  
    // // 이전달 버튼 클릭
    // function prevCalendar(broadcast, radio_name) {
    //     nowMonth = new Date(nowMonth.getFullYear(), nowMonth.getMonth() - 1, nowMonth.getDate());   // 현재 달을 1 감소
    //     buildCalendar(broadcast, radio_name);    // 달력 다시 생성
    // }
    // 다음달 버튼 클릭
    // function nextCalendar(broadcast, radio_name) {
    //     nowMonth = new Date(nowMonth.getFullYear(), nowMonth.getMonth() + 1, nowMonth.getDate());   // 현재 달을 1 증가
    //     buildCalendar(broadcast, radio_name);    // 달력 다시 생성
    // }
  
    prevCal.addEventListener("click", () => {
      nowMonth = new Date(
        nowMonth.getFullYear(),
        nowMonth.getMonth() - 1,
        nowMonth.getDate()
      ); // 현재 달을 1 감소
      buildCalendar(broadcast, radio_name);
    });
    nextCal.addEventListener("click", () => {
      nowMonth = new Date(
        nowMonth.getFullYear(),
        nowMonth.getMonth() + 1,
        nowMonth.getDate()
      ); // 현재 달을 1 증가
      buildCalendar(broadcast, radio_name); // 달력 다시 생성
    });
  
    // input값이 한자리 숫자인 경우 앞에 '0' 붙혀주는 함수
    function leftPad(value) {
      if (value < 10) {
        value = "0" + value;
      }
      return value;
    }
  
    async function fetchData(radio_name, year, month) {
      const response = await fetch(`/api/${broadcast}/${radio_name}/${year}/${month}/all`);
      const data = await response.json();
      console.log("가져온 날짜: ", data);
      // 이후에 data 변수를 사용하는 코드를 작성합니다.
      return data;
    }
  
    function showImg(broadcast, radio_name) {
      const imageUrl = `/api/${broadcast}/${radio_name}/img`;
    
      fetch(imageUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error('이미지를 가져오는 중 오류가 발생했습니다.');
          }
          return response.blob(); // 이미지를 Blob 형태로 가져옴
        })
        .then((imageBlob) => {
          // Blob 데이터를 URL로 변환하여 이미지 요소의 src에 설정
          const mainImgUrl = URL.createObjectURL(imageBlob);
          const radio_img = document.getElementById('radioImg'); // 이미지를 표시할 img 요소
          radio_img.src = mainImgUrl;
        })
        .catch((error) => {
          console.error(error);
          // 오류 처리 로직 추가
        });
    }
    

    function showInfo(radio_name) {
      fetch(`/api/${radio_name}/radio_info`)
        .then((response) => response.json())
        .then((data) => {
          console.log(data)
          radio_info.innerHTML = data.info;
        });
    }
  
    function showLikeCnt(broadcast, radio_name) {
      const likeCountElement = document.getElementById("likecnt");
      fetch(`/api/like-cnt/${broadcast}/${radio_name}`)
        .then((response) => response.json())
        .then((data) => {
          console.log(data)
          likeCountElement.innerHTML = data["like_cnt"];
        });
    }
    function setLikeImage(broadcast, radio_name) {
      // const likeElement = document.getElementById("like");
      const heartImage = document.getElementById("imgControl");
      const cookieValue = getCookie(broadcast, radio_name);
      if (cookieValue === "true") {
        heartImage.src = "/static/images/heart.png";
      } else {
        heartImage.src = "/static/images/before_heart.png";
      }
    }
  
    heartImg.addEventListener("click", function () {
      const likeCountElement = document.getElementById("likecnt");
      // const broadcast = urlParams.get("broadcast").replace(/\/$/, "");
      // const radio_name = urlParams.get("radio_name");
  
      const cookieValue = getCookie(broadcast, radio_name);
  
      if (cookieValue === "true") {
        heartImg.src = "/static/images/before_heart.png";
        const url = `/api/unlike/${broadcast}/${radio_name}`;
        likeCountElement.innerHTML = parseInt(likeCountElement.innerHTML) - 1;
        setCookie(broadcast, radio_name, "false", 365);
  
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
        heartImg.src = "/static/images/heart.png";
        const url = `/api/like/${broadcast}/${radio_name}`;
        likeCountElement.innerHTML = parseInt(likeCountElement.innerHTML) + 1;
        setCookie(broadcast, radio_name, "true", 365);
  
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
      }
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
  };



  return (
    <div id="sub1_wrap">
      <a href="/">
        <div id="logo">
          <img id="logoImg" src="/static/images/logo_opacity0.jpeg" />
        </div>
      </a>
      <div id="content">
        <div id="info">
          <div id="image">
            {/* <!-- 라디오 이미지 --> */}
            <img id="radioImg" src="" />
            <div id="like">
              <img id="imgControl" src="/static/images/heart.png" />
              <span id="likecnt"></span>
            </div>
          </div>
          {/* <!-- 라디오 소개글 --> */}
          <div id="radioInfo"></div>
        </div>
        <div id="episode">
          <table className="calendar">
            <thead>
              <tr>
                <td id="prevCal" style={{cursor:"pointer"}} onClick={handlePrevCalClick}>
                  &#60;
                </td>
                <td colSpan="5">
                  <span id="calYear">{year} </span>년 
                  <span id="calMonth"> {month}</span>월
                </td>
                <td id="nextCal" style={{cursor:"pointer"}} onClick={handleNextCalClick}>
                  &#62;
                </td>
              </tr>
              <tr>
                <td>일</td>
                <td>월</td>
                <td>화</td>
                <td>수</td>
                <td>목</td>
                <td>금</td>
                <td>토</td>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>
  );
};



export default Sub1;
