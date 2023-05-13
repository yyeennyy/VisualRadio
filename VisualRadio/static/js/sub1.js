window.onload = function () { 
    const urlParams = new URLSearchParams(window.location.search);
    const radio_name = urlParams.get('radio_name');
    // console.log(radio_name)
    buildCalendar(radio_name);
    showImg(radio_name);
    showInfo(radio_name); };   // 웹 페이지가 로드되면 buildCalendar 실행

const source = "http://localhost:8080"

let nowMonth = new Date();  // 현재 달을 페이지를 로드한 날의 달로 초기화
let today = new Date();     // 페이지를 로드한 날짜를 저장
today.setHours(0,0,0,0);    // 비교 편의를 위해 today의 시간을 초기화

// 달력 생성 : 해당 달에 맞춰 테이블을 만들고, 날짜를 채워 넣음
function buildCalendar(radio_name) {
    let firstDate = new Date(nowMonth.getFullYear(), nowMonth.getMonth(), 1);     // 이번달 1일
    let lastDate = new Date(nowMonth.getFullYear(), nowMonth.getMonth() + 1, 0);  // 이번달 마지막날

    let year = String(nowMonth.getFullYear()).slice(-2);
    let month = firstDate.getMonth() + 1; // getMonth()는 0부터 시작하므로 1을 더해서 실제 월 값을 얻습니다.
    let tbody_Calendar = document.querySelector(".calendar tbody");
    document.getElementById("calYear").innerText = nowMonth.getFullYear();             // 연도 숫자 갱신
    document.getElementById("calMonth").innerText = leftPad(nowMonth.getMonth() + 1);  // 월 숫자 갱신

    while (tbody_Calendar.rows.length > 0) {                        // 이전 출력 결과가 남아있는 경우 초기화
        tbody_Calendar.deleteRow(tbody_Calendar.rows.length - 1);
    }

    let nowRow = tbody_Calendar.insertRow();        // 첫번째 행 추가           

    for (let j = 0; j < firstDate.getDay(); j++) {  // 이번달 1일의 요일만큼
        let nowColumn = nowRow.insertCell();        // 열 추가
    }
    fetchData(radio_name, month)
    .then(data => {
        let dateOk = data;
        for (let nowDay = firstDate; nowDay <= lastDate; nowDay.setDate(nowDay.getDate() + 1)) {   // day는 날짜를 저장하는 변수, 이번달 마지막날까지 증가시키며 반복  
            let nowColumn = nowRow.insertCell();        // 새 열을 추가하고
            nowColumn.innerText = leftPad(nowDay.getDate());      // 추가한 열에 날짜 입력
            nowColumn.setAttribute("date",  year+leftPad(month)+leftPad(nowDay.getDate()));
            var date = nowDay.getMonth()+1 + "/" + nowDay.getDate();
            for(let i=0; i<dateOk.length; i++){
                if(dateOk[i].date == date){
                    nowColumn.className = "day";
                    nowColumn.addEventListener('click', function(event){
                        let clickDiv = event.currentTarget;
                        let click_date = clickDiv.getAttribute('date');
                        console.log(radio_name)
                        console.log(click_date)
                        fetch(`${source}/${radio_name}/${click_date}/subpage`)
                        .then((response) => response.json())
                        .then((data) => {
                            location.href = data.url;
                        }
                    );
                    })
                }
            }

            if (nowDay.getDay() == 0) {                 // 일요일인 경우 글자색 빨강으로
                nowColumn.style.color = "#DC143C";
            }
            if (nowDay.getDay() == 6) {                 // 토요일인 경우 글자색 파랑으로 하고
                nowColumn.style.color = "#0000CD";
                nowRow = tbody_Calendar.insertRow();    // 새로운 행 추가
            }
        }
    });
}

// 이전달 버튼 클릭
function prevCalendar() {
    nowMonth = new Date(nowMonth.getFullYear(), nowMonth.getMonth() - 1, nowMonth.getDate());   // 현재 달을 1 감소
    buildCalendar();    // 달력 다시 생성
}
// 다음달 버튼 클릭
function nextCalendar() {
    nowMonth = new Date(nowMonth.getFullYear(), nowMonth.getMonth() + 1, nowMonth.getDate());   // 현재 달을 1 증가
    buildCalendar();    // 달력 다시 생성
}

// input값이 한자리 숫자인 경우 앞에 '0' 붙혀주는 함수
function leftPad(value) {
    if (value < 10) {
        value = "0" + value;
        return value;
    }
    return value;
}

async function fetchData(radio_name, month) {
    const response = await fetch(`${source}/${radio_name}/${month+1}/all`);
    const data = await response.json();
    // 이후에 data 변수를 사용하는 코드를 작성합니다.
    return data;
  }

let radio_img = document.getElementById('radioImg')

function showImg(radio_name){
fetch(`${source}/${radio_name}/img`)
.then((response) => response.json())
.then((data) => {
    radio_img.setAttribute('src', data.main_photo)
})}

let radio_info = document.getElementById('radioInfo')


function showInfo(radio_name){
    fetch(`${source}/${radio_name}/radio_info`)
    .then((response) => response.json())
    .then((data) => {
        radio_info.innerHTML = data.info
    })}