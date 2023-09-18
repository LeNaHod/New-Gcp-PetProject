document.body.onload = function(event){
    var path = document.getElementById("path");
    path_list = ["index", "Medical", "services", "mypage", "member", "login"];

    for (var i=0 ; i < path_list.length ;i++){
        var li = document.getElementById(path_list[i]);
        if (li != null) {
        if (path.value.split("/")[1] =="" && i==0) {
            li.className = "active";
            }
        else if (path.value.split("/")[1] == path_list[i]) {
            li.className = "active";
        }
        }
    }


    // views.py 에서 msg 를 보냈다면 toast 메세지로 출력
    const toast = document.getElementById('toast');  // id가 toast인 요소 div
    var msg = document.getElementById('msg');

    let isToastShown = false;
    console.log('msg : ', msg.value)
    if(msg.value != ""){
        if (isToastShown) return;   // 토스트 메시지가 띄어져 있다면 함수를 끝냄
        toast.innerText=msg.value;
        isToastShown = true;
        toast.classList.add('show');    // show라는 클래스를 추가해서 토스트 메시지를 띄우는 애니메이션을 발동시킴
        setTimeout(function () {
            // 2700ms 후에 show 클래스를 제거함
            toast.classList.remove('show');
            isToastShown = false;
        }, 2500);
    }



}

