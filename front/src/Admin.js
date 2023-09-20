//   // import React from "react";
//   // import "./Admin.css";
//   // import { useNavigate } from "react-router-dom";
//   // import { useEffect, useState } from 'react';
//   // import axios from 'axios';
//   //  import "./js/Main.js";

//   // const Admin = () => {
//   //   const [data, setData] = useState([]);
//   //   const navigate = useNavigate();

//   //   const goToHome = () => {
//   //     console.log("he");
//   //     navigate("/");
//   //   };

//   //   const [formData, setFormData] = useState({
//   //     broadcast: '',
//   //     program_name: '',
//   //     date: '',
//   //     audio_file: null,
//   //   });

//   //   const handleChange = (e) => {
//   //     const { name, value, type, files } = e.target;
//   //     const updatedFormData = type === 'file' ? { ...formData, [name]: files[0] } : { ...formData, [name]: value };
//   //     setFormData(updatedFormData);
//   //   };

//   //   const handleSubmit = (e) => {
//   //     e.preventDefault();

//   //     const { broadcast, program_name, date, audio_file } = formData;

//   //     if (!broadcast || !program_name || !date) {
//   //       alert('방송사, 프로그램 이름, 날짜는 필수 값입니다.');
//   //       return;
//   //     }

//   //     alert('제출 완료! 일정 시간 후 콘텐츠 제작이 완료됩니다.');

//   //     axios.get(`/api/${broadcast}/${program_name}/${date}/check_wav`)
//   //       .then((response) => {
//   //         const { wav } = response.data;
//   //         const wavExists = wav === 'true';

//   //         if (wavExists) {
//   //           console.log('[주의!] 서버에 이미 존재하는 wav를 사용합니다.');
//   //           delete formData.audio_file;  audio_file 필드를 FormData에서 제거
//   //         }

//   //         sendForm();
//   //       })
//   //       .catch((error) => {
//   //         console.error('Error checking wav:', error);
//   //       });
//   //   };

//   //   const sendForm = () => {
//   //     const htmlForm = new FormData();
//   //     for (const key in formData) {
//   //       if (formData[key] !== null) {
//   //         htmlForm.append(key, formData[key]);
//   //       }
//   //     }

//   //      이제 htmlForm을 사용하여 데이터를 서버에 보낼 수 있습니다.
//   //     axios.post('/api/admin-updatet', htmlForm)
//   //       .then((response) => {
//   //         console.log('Response from server:', response.data);
//   //       })
//   //       .catch((error) => {
//   //         console.error('Error sending form:', error);
//   //       });
//   //   };
//   //    function submitForm() {
//   //      console.log("hi");
//   //      var htmlForm = document.getElementById("broadcast_form");
//   //      var htmlFormData = new FormData(htmlForm);
//   //      var b = htmlFormData.get("broadcast");
//   //      var p = htmlFormData.get("program_name");
//   //      var d = htmlFormData.get("date");
//   //      if ((b.length == 0) | (p.length == 0) | (d.length == 0)) {
//   //        alert("방송사, 프로그램이름, 날짜는 필수값입니다.");
//   //        return;
//   //      } else {
//   //        alert("제출 완료! 일정 시간 후 콘텐츠 제작이 완료됩니다.");

//   //        var xhrExistCheck = new XMLHttpRequest();
//   //         axios.get(`/api/${b}/${p}/${d}/check_wav`)
//   //        xhrExistCheck.open("GET", `/api/${b}/${p}/${d}/check_wav`);

//   //        xhrExistCheck.onreadystatechange = function () {
//   //          if (xhrExistCheck.readyState === 4 && xhrExistCheck.status === 200) {
//   //            var response = JSON.parse(xhrExistCheck.responseText);
//   //            var wavExists = response.wav === "true";
//   //            if (wavExists) {
//   //              console.log("[주의!] 서버에 이미 존재하는 wav를 사용합니다.");
//   //              htmlFormData.delete("audio_file");
//   //            }
//   //            sendForm(htmlFormData);
//   //          }
//   //        };
//   //        xhrExistCheck.send();
//   //      }
//   //    }
//   //    function sendForm(formData) {
//   //      var xhr = new XML() / apiHttpRequest();
//   //      xhr.open("POST", "/api/admin-update");
//   //      xhr.onreadystatechange = function () {
//   //        if (xhr.readyState === 4 && xhr.status === 200) {
//   //        }
//   //      };
//   //      xhr.send(formData);
//   //    }

//   //   window.onload = () => {
//   //     document.querySelector("#submit").addEventListener("onClick", submitForm);
//   //     console.log(document.querySelector("#submit"));
//   //   };

//   //   return (
//   //     <div id="admin_wrap">
//   //       <a href="/">
//   //         <div id="logo">
//   //           <img id="logoImg" src="/static/images/logo.png" />
//   //         </div>
//   //       </a>
//   //       <div id="info">방송 정보 입력</div>
//   //       <form id="broadcast_form" encType="multipart/form-data" method="POST">
//   //         <table>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="broadcast">방송사</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input
//   //                 className="input"
//   //                 type="text"
//   //                 id="broadcast"
//   //                 name="broadcast"
//   //                 size="20"
//   //               />
//   //             </td>
//   //           </tr>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="program_name">프로그램 이름</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input
//   //                 className="input"
//   //                 type="text"
//   //                 id="program_name"
//   //                 name="program_name"
//   //                 size="20"
//   //               />
//   //             </td>
//   //           </tr>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="program_info">프로그램 정보</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input
//   //                 className="input"
//   //                 type="text"
//   //                 id="program_info"
//   //                 name="program_info"
//   //                 size="20"
//   //               />
//   //             </td>
//   //           </tr>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="date">날짜</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input className="input" type="date" id="date" name="date" />
//   //             </td>
//   //           </tr>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="guest_info">게스트 정보</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input
//   //                 className="input"
//   //                 type="text"
//   //                 id="guest_info"
//   //                 name="guest_info"
//   //                 size="20"
//   //               />
//   //             </td>
//   //           </tr>
//   //           <tr>
//   //             <td className="st">
//   //               <label htmlFor="audio_file">음성 파일</label>
//   //             </td>
//   //             <td className="nd">
//   //               <input type="file" id="audio_file" name="audio_file" size="20" />
//   //             </td>
//   //           </tr>
//   //         </table>
//   //         <button type="button" id="submit" onClick={submitForm}>
//   //           제출
//   //         </button>
//   //       </form>
//   //       <a id="home" onClick={goToHome}>홈으로 돌아가기</a>
//   //     </div>
//   //   );
//   // };

//   // export default Admin;

// import React, { useState } from 'react';
// import axios from 'axios';
// import { useNavigate } from 'react-router-dom';

// const Admin = () => {
//   const navigate = useNavigate();
//   const [formData, setFormData] = useState({
//     broadcast: '',
//     program_name: '',
//     program_info: '',
//     guest_info: '',
//     date: '',
//     audio_file: null,
//   });

//   const handleChange = (e) => {
//     const { name, value, type, files } = e.target;
//     const updatedFormData = type === 'file' ? { ...formData, [name]: files[0] } : { ...formData, [name]: value };
//     setFormData(updatedFormData);
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const { broadcast, program_name, program_info, guest_info, date, audio_file } = formData;

//     if (!broadcast || !program_name || !date) {
//       alert('방송사, 프로그램 이름, 날짜는 필수 값입니다.');
//       return;
//     }

//     alert('제출 완료! 일정 시간 후 콘텐츠 제작이 완료됩니다.');

//     try {
//       const response = await axios.get(`/api/${broadcast}/${program_name}/${date}/check_wav`);
//       const { wav } = response.data;
//       const wavExists = wav === 'true';

//       if (wavExists) {
//         console.log('[주의!] 서버에 이미 존재하는 wav를 사용합니다.');
//         delete formData.audio_file; 
//         //  audio_file 필드를 FormData에서 제거
//       }

//       sendForm();
//     } catch (error) {
//       console.error('Error checking wav:', error);
//     }
//   };

//   const sendForm = async () => {
//     const htmlForm = new FormData();
//     for (const key in formData) {
//       if (formData[key] !== null) {
//         htmlForm.append(key, formData[key]);
//       }
//     }

//     try {
//       const response = await axios.post('/api/admin-update', htmlForm);
//       console.log('Response from server:', response.data);
//     } catch (error) {
//       console.error('Error sending form:', error);
//     }
//   };

//   const goToHome = () => {
//     navigate('/');
//   };

//   return (
//     <div id="admin_wrap">
//       <a href="/">
//         <div id="logo">
//           <img id="logoImg" src="/static/images/logo.png" alt="로고" />
//         </div>
//       </a>
//       <div id="info">방송 정보 입력</div>
//       <form id="broadcast_form" encType="multipart/form-data" method="POST" onSubmit={handleSubmit}>
//         <table>
//           <tbody>
//             <tr>
//               <td className="st">
//                 <label htmlFor="broadcast">방송사</label>
//               </td>
//               <td className="nd">
//                 <input
//                   className="input"
//                   type="text"
//                   id="broadcast"
//                   name="broadcast"
//                   size="20"
//                   value={formData.broadcast}
//                   onChange={handleChange}
//                   required
//                 />
//               </td>
//             </tr>
//             <tr>
//               <td className="st">
//                 <label htmlFor="program_name">프로그램 이름</label>
//               </td>
//               <td className="nd">
//                 <input
//                   className="input"
//                   type="text"
//                   id="program_name"
//                   name="program_name"
//                   size="20"
//                   value={formData.program_name}
//                   onChange={handleChange}
//                   required
//                 />
//               </td>
//             </tr>
//             <tr>
//               <td className="st">
//                 <label htmlFor="program_info">프로그램 정보</label>
//               </td>
//               <td className="nd">
//                 <input
//                   className="input"
//                   type="text"
//                   id="program_info"
//                   name="program_info"
//                   size="20"
//                   value={formData.program_info}
//                   onChange={handleChange}
//                 />
//               </td>
//             </tr>
//             <tr>
//               <td className="st">
//                 <label htmlFor="date">날짜</label>
//               </td>
//               <td className="nd">
//                 <input 
//                   className="input"
//                   type="date"
//                   id="date"
//                   name="date"
//                   value={formData.date}
//                   onChange={handleChange}
//                   required
//                   />
//               </td>
//             </tr>
//             <tr>
//               <td className="st">
//                 <label htmlFor="guest_info">게스트 정보</label>
//               </td>
//               <td className="nd">
//                 <input
//                   className="input"
//                   type="text"
//                   id="guest_info"
//                   name="guest_info"
//                   size="20"
//                   value={formData.guest_info}
//                   onChange={handleChange}
//                 />
//               </td>
//             </tr>
//             <tr>
//               <td className="st">
//                 <label htmlFor="audio_file">음성 파일</label>
//               </td>
//               <td className="nd">
//                 <input
//                   type="file"
//                   id="audio_file"
//                   name="audio_file"
//                   size="20"
//                   value={formData.audio_file}
//                   onChange={handleChange}
//                   />
//               </td>
//             </tr>
//           </tbody>
//         </table>
//         <button type="submit">제출</button>
//       </form>
//       <a id="home" onClick={goToHome}>홈으로 돌아가기</a>
//     </div>
//   );
// };

// export default Admin;

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
  import "./Admin.css";

const Admin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    broadcast: '',
    program_name: '',
    program_info: '',
    guest_info: '',
    date: '',
    audio_file: null,
  });

  const handleChange = (e) => {
    const { name, value, type, files } = e.target;
    const updatedFormData = type === 'file' ? { ...formData, [name]: files[0] } : { ...formData, [name]: value };
    setFormData(updatedFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { broadcast, program_name, program_info, guest_info, date, audio_file } = formData;

    if (!broadcast || !program_name || !date) {
      alert('방송사, 프로그램 이름, 날짜는 필수 값입니다.');
      return;
    }

    alert('제출 완료! 일정 시간 후 콘텐츠 제작이 완료됩니다.');

    try {
      const response = await axios.get(`/api/${broadcast}/${program_name}/${date}/check_wav`);
      const { wav } = response.data;
      const wavExists = wav === 'true';

      if (wavExists) {
        console.log('[주의!] 서버에 이미 존재하는 wav를 사용합니다.');
        // audio_file 필드를 FormData에서 제거
        delete formData.audio_file;
      }

      sendForm();
    } catch (error) {
      console.error('Error checking wav:', error);
    }
  };

  const sendForm = async () => {
    const htmlForm = new FormData();
    console.log(formData)
    for (const key in formData) {
      if (formData[key] !== null) {
        
        htmlForm.append(key, formData[key]);
      }
    }

    console.log(htmlForm)
    try {
      const response = await axios.post('/api/admin-update', htmlForm);
      console.log('Response from server:', response.data);
    } catch (error) {
      console.error('Error sending form:', error);
    }
  };

  const goToHome = () => {
    navigate('/');
  };

  return (
    <div id="admin_wrap">
      <a href="/">
        <div id="logo">
          <img id="logoImg" src="/static/images/logo.png" alt="로고" />
        </div>
      </a>
      <div id="info">방송 정보 입력</div>
      <form id="broadcast_form" encType="multipart/form-data" method="POST" onSubmit={handleSubmit}>
        <table>
          <tbody>
            <tr>
              <td className="st">
                <label htmlFor="broadcast" style={{ fontSize: '15px' }}>방송사</label>
              </td>
              <td className="nd">
                <input
                  className="input"
                  type="text"
                  id="broadcast"
                  name="broadcast"
                  size="20"
                  value={formData.broadcast}
                  onChange={handleChange}
                  required
                />
              </td>
            </tr>
            <tr>
              <td className="st">
                <label htmlFor="program_name" style={{ fontSize: '15px' }}>프로그램 이름</label>
              </td>
              <td className="nd">
                <input
                  className="input"
                  type="text"
                  id="program_name"
                  name="program_name"
                  size="20"
                  value={formData.program_name}
                  onChange={handleChange}
                  required
                />
              </td>
            </tr>
            <tr>
              <td className="st">
                <label htmlFor="program_info" style={{ fontSize: '15px' }}>프로그램 정보</label>
              </td>
              <td className="nd">
                <input
                  className="input"
                  type="text"
                  id="program_info"
                  name="program_info"
                  size="20"
                  value={formData.program_info}
                  onChange={handleChange}
                />
              </td>
            </tr>
            <tr>
              <td className="st">
                <label htmlFor="date" style={{ fontSize: '15px' }}>날짜</label>
              </td>
              <td className="nd">
                <input 
                  className="input"
                  type="date"
                  id="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  size="20"
                  required
                />
              </td>
            </tr>
            <tr>
              <td className="st">
                <label htmlFor="guest_info" style={{ fontSize: '15px' }}>게스트 정보</label>
              </td>
              <td className="nd">
                <input
                  className="input"
                  type="text"
                  id="guest_info"
                  name="guest_info"
                  size="20"
                  value={formData.guest_info}
                  onChange={handleChange}
                />
              </td>
            </tr>
            <tr>
              <td className="st">
                <label htmlFor="audio_file" style={{ fontSize: '15px' }}>음성 파일</label>
              </td>
              <td className="nd">
                <input
                  type="file"
                  id="audio_file"
                  name="audio_file"
                  size="20"
                  style={{ fontSize: '15px' }}
                  onChange={handleChange}
                />
              </td>
            </tr>
          </tbody>
        </table>
        <button type="submit" style={{ fontSize: '15px' }}>제출</button>
      </form>
      <a id="home" onClick={goToHome} style={{ fontSize: '15px' }}>홈으로 돌아가기</a>
    </div>
  );
};

export default Admin;
