var bmodal = document.getElementById('birthdayModal')
var wmodal = document.getElementById('weddingModal')
var omodal = document.getElementById('otherModal')
var bbtn = document.getElementById('birthday')
var wbtn = document.getElementById('wedding')
var obtn = document.getElementById('other')
bbtn.onclick = function (){
    bmodal.style.display = "block";
}

wbtn.onclick = function (){
    wmodal.style.display = "block";
}

obtn.onclick = function (){
    omodal.style.display = "block";
}

window.onclick = function(event) {
    if (event.target == bmodal) {
      bmodal.style.display = "none";
    }else if(event.target == wmodal){
        wmodal.style.display = "none";
    }else if(event.target == omodal){
        omodal.style.display = "none";
    }
  }