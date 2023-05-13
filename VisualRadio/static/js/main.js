const source = "http://localhost:8080"

const mbcElements = document.getElementsByClassName("cover");
const mbcImgElements = document.getElementsByClassName("mbcFm4u_img");

function getInfo() {
    return fetch(`${source}/radio`)
    .then((response) => response.json())
    .then((data) => 
        {
            // 이 부분 아직 mbc만 초점을 맞춰서 구성되어 있음! 나중에는 들어온 데이터별로 방송사를 다르게
            // 설정할 수 있도록 고쳐야함.
            for(let i=0; i<data.length; i++){
                mbcElements[i].broadcast =  data[i].broadcast;
                mbcElements[i].innerHTML = `<img class="imgControl mbcFm4u_img" src = "${data[i].radio_img_url}" > ${data[i].radio_name}`;
                mbcElements[i].radio_name =  data[i].radio_name;

                mbcElements[i].addEventListener('click' , function(event){
                    let clickDiv = event.currentTarget;
                    let radio_name = clickDiv.radio_name;
                    fetch(`${source}/subpage/${radio_name}`)
                    .then((response) => response.json())
                    .then((data) => {
                        location.href = data.url;
                    }
                );})
            }
        });
}
getInfo();