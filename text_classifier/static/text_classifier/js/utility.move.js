

function getColorByBaiFenBiMove(bili){
    var one = (255+255) / 100;
    var r=0;
    var g=0;
    var b=0;
    if ( bili < 50 ) {
        g = one * bili;
        r=255;
    }
    if ( bili >= 50 ) {
        r =  255 - ( (bili - 50 ) * one) ;
        g = 255;
    }
    r = parseInt(r);
    g = parseInt(g);
    b = parseInt(b);
    return "rgb("+r+","+g+","+b+")";
}

function drawResult(sent_conf) {
    sent_conf = parseInt(sent_conf*100);
    console.log(sent_conf);
    var elem1 = document.getElementById("myBar1");
    var elem2 = document.getElementById("myBar2");
    elem1.style.backgroundColor = getColorByBaiFenBiMove(sent_conf);
    elem2.style.backgroundColor = getColorByBaiFenBiMove(100-sent_conf);
    var width1 = 0;
    var width2 = 0;
    var id1 = setInterval(frame1, 450/(sent_conf));
    var id2 = setInterval(frame2, 450/(100-sent_conf));

    function frame1() {
      if (width1 >= (sent_conf)) {
        clearInterval(id1);
      }
      else {
        width1++;
        elem1.style.width = width1 + '%';
        elem1.innerHTML = width1 * 1  + '%';
      }
    }
    function frame2() {
      if (width2 >= (100-sent_conf)) {
        clearInterval(id2);
      }
      else {
        width2++;
        elem2.style.width = width2 + '%';
        elem2.innerHTML = width2 * 1  + '%';
      }
    }
}
  // var sent_conf = parseInt(document.getElementById("sent_conf").value*100);
  // console.log(sent_conf);
