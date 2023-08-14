function searchBroadcasts() {
    const searchInput = document.getElementById("searchInput").value;
    
    // 이 부분에서 서버로 검색어를 전송하고 결과를 받아온다고 가정합니다.
    // 서버에서 받아온 데이터는 아래와 같은 형식일 것입니다.

    var programUrl = '/tmp_paragraph/search/' + searchInput;
    var serverData
    fetch(programUrl)
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            serverData = data;

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = ""; // 결과를 표시하기 전에 이전 결과를 지웁니다.
            
            // 검색 결과를 HTML로 생성하여 결과 창에 추가합니다.
            serverData.forEach(data => {
            const resultItem = document.createElement("div");
            resultItem.classList.add("result-item");
            resultItem.innerHTML = `
                <p><strong>방송국:</strong> ${data.broadcast}</p>
                <p><strong>프로그램:</strong> ${data.radio_name}</p>
                <p><strong>방영일:</strong> ${data.radio_date}</p>
                <p><strong>time:</strong> ${data.time}</p>
                <p><strong>Content:</strong> ${data.content}</p>
                <p>----------------------------------</p>
            `;
            resultsDiv.appendChild(resultItem);
        });
    });

  }
  