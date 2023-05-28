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
