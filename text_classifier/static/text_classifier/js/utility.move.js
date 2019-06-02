

  var sent_conf = parseInt(document.getElementById("sent_conf").value*100);

  var elem1 = document.getElementById("myBar1");
  var elem2 = document.getElementById("myBar2");
  var pp = sent_conf;
  console.log(pp);

  var width1 = 0;
  var width2 = 0;
  var id1 = setInterval(frame1, 450/(100-pp));
  var id2 = setInterval(frame2, 450/pp);

  function frame1() {
    if (width1 >= (100-pp)) {
      clearInterval(id1);
    }
    else {
      width1++;
      elem1.style.width = width1 + '%';
      elem1.innerHTML = width1 * 1  + '%';
    }
  }
  function frame2() {
    if (width2 >= pp) {
      clearInterval(id2);
    }
    else {
      width2++;
      elem2.style.width = width2 + '%';
      elem2.innerHTML = width2 * 1  + '%';
    }
  }
