const channelsElement = document.getElementById("resultchannels");
const resultTextTitle = document.getElementById("resultTextTitle");
const resultContainer = document.getElementById("resultContainer");
const channels = document.getElementById("channels");

document.getElementById('searchForm').addEventListener('submit', function(event) {
    // 선택옵션 가져오기
    var searchOptionRadios = document.getElementsByName("searchOption");
    var option;

    resultTextTitle.style.display = 'block';
    resultContainer.style.display = 'flex';
    channels.style.display = 'none';

    for (var i = 0; i < searchOptionRadios.length; i++) {
    if (searchOptionRadios[i].checked) {
            option = searchOptionRadios[i].value;
            break;
        }
    }
    document.getElementById("resultchannels").innerHTML="";

    document.getElementById("resultText").textContent="";
    event.preventDefault(); // 폼 제출 기본 동작 막기
    var searchInput = document.getElementById('searchInput').value;
    if (searchInput == ''){
        var resultElement = document.getElementById("resultText");
        var textToInsert = "검색어를 입력하세요 🤔";
        resultElement.textContent = textToInsert;
        resultElement.style.color = "red";
        return
    }
    var queryString = "search=" + searchInput
    var url = '/search/' + option + '?' + queryString;
    fetch(url)
        .then(function(response) {
            var resultText = document.getElementById("resultTextTitle");
            resultText.textContent = "'" + searchInput + "' 검색결과"  
            return response.json();
        })
        .then(function(data) {
            if (data == "[]"){
                var resultText = document.getElementById("resultText");
                resultText.textContent = "검색 결과가 없습니다 📻";
                resultText.style.color = "black";
            } else {
                var parsedData = JSON.parse(data); // 문자열을 JSON 객체로 파싱
                displaySearchResults(parsedData, option);
            }
        })
        .catch(function(error) {
            console.log(error);
        });
});

function displaySearchResults(item, option) {
    console.log(item, option)
    if (option=='program'){
        item.forEach(({broadcast, programs}) => {
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
            })
            channelsElement.appendChild(radioBroadcastElement);
        });
    } else if (option=='listener'){
        item.forEach(({broadcast, radio_name, radio_date, preview_text}) => {
            console.log(radio_date)
            console.log("=================================================")
            const newElement = document.createElement('div');
            newElement.innerHTML = `
                <div>
                    <div class="listenerInfo" broadcast="${broadcast}" radio_name="${radio_name}" radio_date="${radio_date}">${broadcast} | ${radio_name} | ${radio_date} | ${preview_text}</div>
                </div><br>
            `;
            channelsElement.appendChild(newElement)
                // 클릭 이벤트 추가
                newElement.addEventListener("click", function (event) {
                    const clickDiv = event.currentTarget;
                    const radio_name = clickDiv.querySelector(".listenerInfo").getAttribute("radio_name");
                    const broadcast = clickDiv.querySelector(".listenerInfo").getAttribute("broadcast");
                    const radio_date = clickDiv.querySelector(".listenerInfo").getAttribute("radio_date");
                    console.log(broadcast)
                    console.log(radio_name)
                    console.log(radio_date)
                    window.location.href = "/contents?broadcast=" + broadcast + "&radio_name=" + radio_name+"&date="+radio_date;
                });
        });
    }
}

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