window.onload = function () { 
    start()
};   // 웹 페이지가 로드되면 buildCalendar 실행

function start() {
    return fetch("/all")
      .then(response => response.json())
      .then(data => {
        // 버튼 리스트 생성
        var buttonList = "";
        var processPromises = []; // get_process 프라미스 배열
  
        data.forEach(function (element) {
          var processPromise = get_process(element.broadcast, element.radio_name, element.date)
            .then(result => {
              var process = result;
              return process;
            });
          processPromises.push(processPromise);
        });
  
        // 모든 get_process 프라미스를 병렬 실행하고 결과를 기다림
        return Promise.all(processPromises)
          .then(processResults => {
            buttonList = buttonList.replace(/<br><br>$/, ''); // 버튼 리스트 마지막 줄바꿈 제거
  
            // 버튼 리스트에 각각의 process 결과 추가
            for (let i = 0; i < processResults.length; i++) {
              buttonList += '<button onclick="onButtonClick(\'' + data[i].broadcast + '\', \'' + data[i].radio_name + '\', \'' + data[i].date + '\')">'
                            + data[i].broadcast + ' - ' + data[i].radio_name + ' - ' +  data[i].date + '</button> ' + processResults[i] + ' <br><br>';
            }
  
            document.getElementById('button-list').innerHTML = buttonList;
  
            return data;
          });
      });
  }
  
  function get_process(broadcast, radio_name, radio_date) {
    return fetch(`/${broadcast}/${radio_name}/${radio_date}/get_process`)
      .then(response => response.json())
      .then(data => {
        if(data.end == 0){
            return "split 1 진행 중..."
        }else if(data.end == 1){
            return "split 2 진행 중..."
        }else if(data.end == data.all-2){
            return "script 생성 중..."
        }else if(data.end == data.all-1){
            return "script 합치는 중..."
        }else if(data.end == data.all){
            return "오디오 처리 완료!!"
        }else{
            return "stt 진행 중... "+(parseInt(data.end)-2) + "/"+ (parseInt(data.all)-4);
        }
      });
  }
  
// 버튼 클릭 이벤트 처리
function onButtonClick(broadcast, radio_name, date) {
    window.location.href = '/sub2?broadcast=' + broadcast + '&radio_name=' + radio_name + '&date=' + date;
}

