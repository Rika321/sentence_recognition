function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
})

var send = {
	'sentence': 'good'
};

var sorted_data;

var barColor = {};

var compare = function(a,b) {
	if(Math.abs(a[1])<Math.abs(b[1]))
		return -1;
	else
		return 1;
}

$(document).on("click", "#explain_btn", function(e) {
	$.ajax({
		url: "../explain",
		// headers: headers,
		type: "POST",
		data: send,
		success: function(data) {
			keys = Object.keys(data);
			sorted_data = new Array(keys.length);
			var i=0;
			for(i=0;i<sorted_data.length;i++) {
				sorted_data[i] = new Array(keys[i],data[keys[i]]);
			}
			sorted_data = sorted_data.sort(compare);
			drawBar(sorted_data);
			//TODO
		},
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url))
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	    }
	})
});


function getColorByBaiFenBi(bili){
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

function drawBar(sorted_data) {
	var barPlus = document.createElement("canvas");
	barPlus.innerHTML = "Your browser does not support the HTML5 canvas tag."
	barPlus.width = "600"
	barPlus.height = "25"
	$("#bar_plus").append(barPlus); 
	var barMinus = barPlus.cloneNode(true)
	$("#bar_minus").append(barMinus); 
	barPlus = barPlus.getContext("2d");
	barMinus = barMinus.getContext("2d");
	var ctx = new Array(barPlus, barMinus);
	var start = new Array(0, 0);
	var len = 0;
	var totalLen = 600;
	var id = 0;
	var total = 0;
	var min = new Array(1000000, 1000000);
	var max = new Array(0, 0);
	for(let a of sorted_data) {
		var temp = Math.abs(a[1]);
		total += temp;
		if(a[1]>0)
			id = 0;
		else
			id = 1;
		min[id] = Math.min(min[id], temp);
		max[id] = Math.max(max[id], temp);
	}
	for(let a of sorted_data) {
		if(a[1]>0)
			id = 0;
		else
			id = 1;
		len = totalLen*Math.abs(a[1])/total;
		// console.log(a[1]+" "+len);
		ctx[id].lineWidth="2";
		var part = 50;
		if(max[id]!=min[id])
			part = parseInt((Math.abs(a[1])-min[id])/(max[id]-min[id])*50);
		// console.log(part);
		if(id==1)
			part = -part;
		part += 50;
		ctx[id].fillStyle=getColorByBaiFenBi(part);
		barColor[a[0]] = ctx[id].fillStyle;
		ctx[id].fillRect(start[id],0,len,25);
		ctx[id].fillStyle="#000000";
		ctx[id].rect(start[id],0,len,25);
		ctx[id].stroke();
		start[id] += len
	}
	$(".explain").show();
}