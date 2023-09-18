function showImage(files) {
console.log(files[0]);
renderFile(files[0]);


  function renderFile(file) {

  let reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = function () {
  var img_div = document.getElementById('imgDiv');
    console.log("dev 찾음", img_div);
    console.log("reader.result : ", reader.result)
  img_div.src = reader.result;
  console.log('실행완료')
  }
  }

}


