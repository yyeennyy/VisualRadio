// // 쿠키 저장
// window.setCookie = function(broadcast, radio_name, value, days) {
//     const cookieName = broadcast + radio_name;
//     const expires = new Date();
//     expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
//     document.cookie = cookieName + "=" + value + ";expires=" + expires.toUTCString() + ";path=/";
// };

// // 쿠키 읽기
// window.getCookie = function(broadcast, radio_name) {
//     const cookieName = broadcast + radio_name;
//     const value = document.cookie.match('(^|;) ?' + cookieName + '=([^;]*)(;|$)');
//     return value ? decodeURIComponent(value[2]) : null;
// };

window.setCookie = function(broadcast, radio_name, value, days) {
    const cookieName = `${broadcast}_${radio_name}`;
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + days);
    const cookieValue = `${value}; expires=${expirationDate.toUTCString()}`;
    document.cookie = `${cookieName}=${cookieValue}`;
  }

window.getCookie = function(broadcast, radio_name) {
  const cookieName = `${broadcast}_${radio_name}`;
  const cookieValue = document.cookie
    .split('; ')
    .find(cookie => cookie.startsWith(`${cookieName}=`));

  if (cookieValue) {
    const value = cookieValue.split('=')[1];
    return value;
  }
  
  return null;
}

// // 쿠키 존재 체크
// window.checkCookie = function(broadcast, radio_name) {
//   const cookieValue = getCookie(broadcast, radio_name); // 쿠키 값 가져오기

//   if (cookieValue !== "") { // 쿠키 값이 이미 존재하는 경우
//       heartImg.src = "/static/images/heart.png";
//   } else { // 쿠키 값이 존재하지 않는 경우
//       heartImg.src = "/static/images/before_heart.png";
//   }
// }