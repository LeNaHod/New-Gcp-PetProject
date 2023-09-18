// 비밀번호와 비밀번호 재확인란을 동일하게 입력했는지 확인
var check = document.getElementById("inputpassword_check");

check.oninput = function password(event){
    var password = document.getElementById("password");
   var check_feedback = document.getElementById("check_feedback");


    if (password.value != check.value) {        // 비밀번호 재확인을 다르게 입력한 경우
        check_feedback.style.display="block";
        check.className="form-control is-invalid";
    } else {                                                             // 비밀번호 맞게 입력한 경우
        check_feedback.style.display="none";
        check.className="form-control is-valid";
    }
  }


