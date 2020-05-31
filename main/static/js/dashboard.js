function openTab(evt, tabName){
    var tabcontent=document.getElementsByClassName('tabContent');
    var tablink=document.getElementsByClassName('tablink')

    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    for (i = 0; i < tablink.length; i++) {
        tablink[i].className = tablink[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
document.getElementById("default").click();