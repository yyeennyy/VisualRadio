const resultTextTitle = document.getElementById("resultTextTitle");
const resultContainer = document.getElementById("resultContainer");
const programsElement = document.getElementById("resultPrograms");
const channels = document.getElementById("channels");
// const menu = document.getElementById("searchMenu");
const ul = document.querySelector("ul");
const result = document.getElementById("result");
const h = document.getElementById("h");
const r = document.getElementById("r");
const resultBox = document.getElementById("resultBox");

document.getElementById('searchForm').addEventListener('submit', function(event) {
    // 선택옵션 가져오기
    // var searchOptionRadios = document.getElementsByName("searchOption");
    // var option;

    resultTextTitle.style.display = 'block';
    resultContainer.style.display = 'block';
    channels.style.display = 'none';
    // menu.style.display = 'block';
    ul.style.display = 'block';
    h.style.display = 'block';
    r.style.display = 'block';
    // resultBox.style.display = 'block';


    // for (var i = 0; i < searchOptionRadios.length; i++) {
    //     if (searchOptionRadios[i].checked) {
    //             option = searchOptionRadios[i].value;
    //             break;
    //         }
    // }
    // document.getElementById("resultchannels").innerHTML="";
    // document.getElementById("resultText").textContent="";

    event.preventDefault(); // 폼 제출 기본 동작 막기
    
    var searchInput = document.getElementById('searchInput').value;
    
    if (searchInput == ''){
        result.style.display = 'none';
        var resultElement = document.getElementById("resultText");
        window.alert("검색어를 입력하세요 🤔");
        // resultElement.style.color = "red";
        return
    }

    var programUrl = '/search/program/' + searchInput;
    // console.log(programUrl)
    var userUrl = '/search/listener/' + searchInput;
    var contentsUrl = '/search/contents/'+ searchInput;

    fetch(programUrl)
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            var resultText = document.getElementById("resultTextTitle");
            resultText.textContent = "'" + searchInput + "' 검색결과"  
            if (data == "[]"){
                const resultProgram = document.getElementById('a');
                resultProgram.textContent = "검색 결과가 없습니다 📻";
                resultText.style.color = "black";
                result.style.display = 'none';
            } else {
                var parsedData = JSON.parse(data); // 문자열을 JSON 객체로 파싱
                showProgramResults(parsedData); 
            }
        });

    fetch(userUrl)
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        var resultText = document.getElementById("resultTextTitle");
        resultText.textContent = "'" + searchInput + "' 검색결과"  
        if (data == "[]"){
            const resultProgram = document.getElementById('a');
            resultProgram.textContent = "검색 결과가 없습니다 📻";
            resultText.style.color = "black";
            result.style.display = 'none';
        } else { // 문자열을 JSON 객체로 파싱
            showUserResults(data);
        }
    });


    fetch(contentsUrl)
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        var resultText = document.getElementById("resultTextTitle");
        resultText.textContent = "'" + searchInput + "' 검색결과"  
        if (data == "[]"){
            const resultProgram = document.getElementById('a');
            resultProgram.textContent = "검색 결과가 없습니다 📻";
            resultText.style.color = "black";
            result.style.display = 'none';
        } else { // 문자열을 JSON 객체로 파싱
            showContentResults(data);
        }
    });
});


// function displaySearchResults(item, option) {
//     console.log(item, option)
//     if (option=='program'){
//         item.forEach(({broadcast, programs}) => {
//             const radioBroadcastElement = createRadioBroadcast(broadcast);
//             programs.forEach((program) => {
//                 const programElement = createProgramElement(program, broadcast);
//                 radioBroadcastElement.appendChild(programElement);
//                     // 클릭 이벤트 추가
//                     programElement.addEventListener("click", function (event) {
//                         const clickDiv = event.currentTarget;
//                         const radio_name = clickDiv.querySelector(".program_name").getAttribute("radio_name");
//                         const broadcast = clickDiv.querySelector(".program_name").getAttribute("broadcast");
//                         window.location.href = "/subpage?broadcast=" + broadcast + "&radio_name=" + radio_name;
//                     });
//             })
//             channelsElement.appendChild(radioBroadcastElement);
//         });
//     } else if (option=='listener'){
//         item.forEach(({broadcast, radio_name, radio_date, preview_text}) => {
//             console.log(radio_date)
//             console.log("=================================================")
//             const newElement = document.createElement('div');
//             newElement.innerHTML = `
//                 <div>
//                     <div class="listenerInfo" broadcast="${broadcast}" radio_name="${radio_name}" radio_date="${radio_date}">${broadcast} | ${radio_name} | ${radio_date} | ${preview_text}</div>
//                 </div><br>
//             `;
//             channelsElement.appendChild(newElement)
//                 // 클릭 이벤트 추가
//                 newElement.addEventListener("click", function (event) {
//                     const clickDiv = event.currentTarget;
//                     const radio_name = clickDiv.querySelector(".listenerInfo").getAttribute("radio_name");
//                     const broadcast = clickDiv.querySelector(".listenerInfo").getAttribute("broadcast");
//                     const radio_date = clickDiv.querySelector(".listenerInfo").getAttribute("radio_date");
//                     console.log(broadcast)
//                     console.log(radio_name)
//                     console.log(radio_date)
//                     window.location.href = "/contents?broadcast=" + broadcast + "&radio_name=" + radio_name+"&date="+radio_date;
//                 });
//         });
//     }
// }

// function displaySearchResults(item) {
//     item.forEach(({broadcast, programs}) => {
//         const radioBroadcastElement = createRadioBroadcast(broadcast);
//         programs.forEach((program) => {
//             const programElement = showProgramResults(program, broadcast);
//             radioBroadcastElement.appendChild(programElement);
//                 // 클릭 이벤트 추가
//                 programElement.addEventListener("click", function (event) {
//                     const clickDiv = event.currentTarget;
//                     const radio_name = clickDiv.querySelector(".program_name").getAttribute("radio_name");
//                     const broadcast = clickDiv.querySelector(".program_name").getAttribute("broadcast");
//                     window.location.href = "/subpage?broadcast=" + broadcast + "&radio_name=" + radio_name;
//                 });
//         })
//         programsElement.appendChild(radioBroadcastElement);
//     });
// }

// function createRadioBroadcast(broadcast) {
//     const radioBroadcastElement = document.createElement("div");
//     radioBroadcastElement.classList.add("resultProgram");
//     radioBroadcastElement.innerHTML = `
//       <div class="radioBroadcastName">${broadcast}</div>
//     `;
//     return radioBroadcastElement;
//   }

function displayProgramResults(program, broadcast) {
    // console.log(program)
    // const { radio_name, img } = program;
    const radio_name = program.radio_name;
    const img = program.img;
    const programElement = document.createElement("div");
    programElement.classList.add("resultProgram");
    const radio_class = radio_name.replace(/\s/g, "")
    // programElement.classList.add(radio_class);
    programElement.innerHTML =`
    <div class = "section1">
        <div class="cover_back median">
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
    </div>
    <div class = "section2">
        <div class = "resultProgramSet">
            <div class="resultProgram_broadcast tmp">${broadcast}</div>
            <div class="resultProgram_radioName tmp" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
        </div>
    </div>
    `;
    return programElement;
  }

function showProgramResults(item) {
    const radioBroadcastElement = document.getElementById('resultPrograms');
    radioBroadcastElement.innerHTML = ''; // 이전 검색 결과를 제거
    item.forEach(({broadcast, programs}) => {
        programs.forEach((program) => {
            const programElement = displayProgramResults(program, broadcast);
            radioBroadcastElement.appendChild(programElement);
        });
    })
}

function showUserResults(item) {
    var searchInput = document.getElementById('searchInput').value;
    const resultUsersElement = document.querySelector('.resultUsers');
    resultUsersElement.innerHTML = ''; // 이전 검색 결과를 제거
    item.forEach(({broadcast, radio_name, radio_date, preview_text}) => {
        console.log(broadcast)
        console.log(radio_name)
        console.log(radio_date)
        console.log(preview_text)
        const newElement = document.createElement('div');
        newElement.classList.add("resultUser");
        newElement.innerHTML = `
        <table class = "userTable">
            <tr>
                <td class = "resultUser_user">${searchInput}님,</td>
                <td class = "resultUser_broadcast">${broadcast}</td>
                <td class = "resultUser_radioName">${radio_name}</td>
                <td class = "resultUser_radioDate">${radio_date}</td>
            </tr>
        </table>
        <div class = "resultUser_preView">${preview_text}</div>
        `;
        resultUsersElement.appendChild(newElement)
        // 클릭 이벤트 추가
        newElement.addEventListener("click", function (event) {
            const clickDiv = event.currentTarget;
            const radio_name = clickDiv.querySelector(".resultUser_radioName").textContent;
            const broadcast = clickDiv.querySelector(".resultUser_broadcast").textContent;
            const radio_date = clickDiv.querySelector(".resultUser_radioDate").textContent;
            const preview_text = clickDiv.querySelector(".resultUser_preView").textContent;
            // console.log(broadcast)
            // console.log(radio_name)
            // console.log(radio_date)
            window.location.href = "/contents?broadcast=" + broadcast + "&radio_name=" + radio_name+"&date="+radio_date;
        });
    });
}


function showContentResults(content) {
    const resultUsersElement = document.querySelector('.resultContents');
    resultUsersElement.innerHTML = ''; // 이전 검색 결과를 제거
    content.forEach(({broadcast, radio_name, radio_date, contents}) => {
        console.log(broadcast)
        console.log(radio_name)
        console.log(radio_date)
        console.log(contents)
        const newElement = document.createElement('div');
        newElement.classList.add("resultContent");
        newElement.innerHTML = `
        <div class = "resultContent">
            <table class = "contentsTable">
                <tr>
                    <td class = "resultContents_broadcast">${broadcast}</td>
                    <td class = "resultContents_radioName">${radio_name}</td>
                    <td class = "resultContents_radionDate">${radio_date}</td>
                </tr>
            </table>
            <div class = "resultContents_preView">${contents}</div>
        </div>
        `;
        resultUsersElement.appendChild(newElement)
        // 클릭 이벤트 추가
        newElement.addEventListener("click", function (event) {
            const clickDiv = event.currentTarget;
            const radio_name = clickDiv.querySelector(".resultContents_broadcast").textContent;
            const broadcast = clickDiv.querySelector(".resultContents_radioName").textContent;
            const radio_date = clickDiv.querySelector(".resultContents_radionDate").textContent;
            const contents = clickDiv.querySelector(".resultContents_preView").textContent;
            // console.log(broadcast)
            // console.log(radio_name)
            // console.log(radio_date)
            window.location.href = "/contents?broadcast=" + broadcast + "&radio_name=" + radio_name+"&date="+radio_date;
        });
    });
    // const {broadcast, radio_name, radio_date, contents} = content
    // const resultContents = document.createElement("div");
    // resultContents.classList.add("resultContents");
    // resultContents.innerHTML = `
    // <div class = "resultContent">
    //     <table class = "contentsTable">
    //         <tr>
    //             <td class = "resultContents_broadcast">${broadcast}</td>
    //             <td class = "resultContents_radioName">${radio_name}</td>
    //             <td class = "resultContents_radionDate">${radio_date}</td>
    //         </tr>
    //     </table>
    //     <div class = "resultContents_preView">${contents}</div>
    // </div>
    // `;

    // return resultContents;
}

    
    
// function createRadioBroadcast(broadcast, radio_class, radio_name) {
//   const radioBroadcastElement = document.createElement("div");
//   radioBroadcastElement.classList.add("resultProgram");
//   radioBroadcastElement.innerHTML =`
//   <div class = "section1">
//       <div class="cover_back median">
//           <div class="lp">
//               <img class="imgControl" src="/static/images/lp.png">
//           </div>
//           <div class="cover">
//               <img class="imgControl" src="${img}">
//           </div>
//           <div class="like">
//               <img class="imgControl" src="/static/images/before_heart.png">
//           </div>
//       </div>
//   </div>
//   <div class = "section2">
//       <div class = "resultProgramSet">
//           <div class="resultProgram_broadcast tmp">${broadcast}</div>
//           <div class="resultProgram_radioName tmp" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
//       </div>
//   </div>
//
//   `;
//   return radioBroadcastElement;
// }

// function createProgramElement(program, broadcast) {
//   const { radio_name, img } = program;
//   const programElement = document.createElement("div");
//   programElement.classList.add("content");
//   const radio_class = radio_name.replace(/\s/g, "")
//   programElement.classList.add(radio_class);
//   programElement.innerHTML = `
//     <div class="cover_back">
//       <div class="lp">
//         <img class="imgControl" src="/static/images/lp.png">
//       </div>
//       <div class="cover">
//         <img class="imgControl" src="${img}">
//       </div>
//       <div class="like">
//         <img class="imgControl" src="/static/images/before_heart.png">
//       </div>
//     </div>
//     <div class="program_name" broadcast="${broadcast}" radio_name="${radio_class}">${radio_name}</div>
//   `;
//   return programElement;
