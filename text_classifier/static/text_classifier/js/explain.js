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
	sentence: $("#sentence").text().split(": ")[1]
}

var sorted_data;

var barColor = {};

var barPos = {};

var compare = function(a,b) {
	if(a[1]>0 && b[1]>0)
		if(a[1]>b[1])
			return 1;
		else
			return -1;
	else if(a[1]<0 && b[1]<0)
		if(a[1]<b[1])
			return 1;
		else
			return -1;
	else
		if(a[1]>b[1])
			return 1;
		else
			return -1;
}

$(document).on("click", "#explain_btn", function(e) {
	if($("#bar_plus").children("div").length>0) {
        $(".explain").show();
		return;
    }
	$.ajax({
		url: "../explain",
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
			drawBar();
			drawTable();
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

function drawBar() {
    var barContext = new Array($("#bar_plus"), $("#bar_minus"));
	var len = 0;
	var totalLen = $("#container").width()-200;
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
    var mark1 = 0;
    var mark2 = 0;
	for(let a of sorted_data) {
		if(a[1]>0)
			id = 0;
		else
			id = 1;
		len = totalLen*Math.abs(a[1])/total;
		var part = 50;
		if(max[id]!=min[id])
			part = parseInt((Math.abs(a[1])-min[id])/(max[id]-min[id])*50);
		if(id==1)
			part = -part;
		part += 50;
		var color = getColorByBaiFenBi(part);
		barColor[a[0]] = color;
        var subBar = document.createElement("div");
        subBar.className = "draw_bar";
        subBar.style.width = parseInt(len)+"px";
        subBar.style.height = "25px";
        subBar.style.background = color;
        subBar.style.display = "inline-block";
        var lineWidth = "1px";
        subBar.style.borderTop = lineWidth+" solid #000";
        subBar.style.borderBottom = lineWidth+" solid #000";
        if(a[1]>0) {
            if(mark1==0) {
                subBar.style.borderLeft = lineWidth+" solid #000";
                mark1 = 1;
            }
        }
        if(a[1]<0) {
            if(mark2==0) {
                subBar.style.borderLeft = lineWidth+" solid #000";
                mark2 = 1;
            }
        }
        subBar.style.borderRight = lineWidth+" solid #000";
        subBar.title = a[0]+"<br/>"+a[1].toFixed(2);
        $(subBar).poshytip();
        barContext[id].append(subBar);
	}
	$(".explain").show();
}

function drawTable() {
	el = $("#explain_table");
	for(i=sorted_data.length-1;i>=0;i--) {
		var color = document.createElement("canvas");
		color.innerHTML = "Your browser does not support the HTML5 canvas tag."
		color.width = "25"
		color.height = "25"
		ctx = color.getContext("2d");
		ctx.fillStyle = barColor[sorted_data[i][0]];
		ctx.fillRect(0,0,25,25);
		var tr = document.createElement("tr");
		$(tr).append("<td></td><td>"+sorted_data[i][0]+"</td><td>"+
			sorted_data[i][1]+"</td>")
		$(tr).children("td")[0].append(color);
		el.append(tr);
	}
}

$(document).on("click", "#plot_btn", function(e) {
	$.ajax({
		url: "../plot",
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
            console.log(sorted_data)
			// sorted_data = sorted_data.sort(compare);
			drawAdjustableBar(sorted_data);
			//TODO
		},
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url))
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	    }
	})
});

function getColor(value, threshold){
    var contri = parseFloat(value);
    if (contri >= threshold){
        contri = threshold;
    }else if (contri <= -threshold) {
        contri = -threshold;
    }
    contri += threshold;
    var percentage = parseInt(contri/(threshold*2)*100.0);
    var color = getColorByBaiFenBi(percentage);
    return color;
}


var dataPoints = [];
function drawAdjustableBar(sorted_data) {
    $(".plot").show();
    console.log("drawbar!");
    // var dataPoints = [];
    var totalDataPoints = []
    var myColors =[];
    var threshold = 2.0;
    $.each(sorted_data, function(key, value){
        var score = value[1][0];
        var freq  = value[1][1];
        var color = getColor(score, threshold);
        var label1 = "("+value[0]+")" + "*"+ String(freq);
        dataPoints.push({label: value[0], y: parseFloat(score),color:color, freq: freq});
        var total = score * freq;
        var totCol = getColor(total, threshold);
        totalDataPoints.push({label: value[0], y: parseFloat(total),color:totCol});
    });

    var chart = new CanvasJS.Chart("chartContainer",
    {
        title: {
            text: "Gram Analysis",
        },
        data: [{
    		type: "column",
    		legendText: "Individual Word Contribution",
    		showInLegend: true,
    		dataPoints:dataPoints
    	}
        ]
    });
    chart.render();
    // chart2.render();
    var xSnapDistance = chart.axisX[0].convertPixelToValue(chart.get("dataPointWidth")) / 2;
    var ySnapDistance = 800;
    var xValue, yValue;
    var mouseDown = false;
    var selected = null;
    var changeCursor = false;
    var timerId = null;
    function getPosition(e) {
        var parentOffset = $("#chartContainer > .canvasjs-chart-container").offset();
        var relX = e.pageX - parentOffset.left;
        var relY = e.pageY - parentOffset.top;
        xValue = Math.round(chart.axisX[0].convertPixelToValue(relX));
        yValue = Math.round(chart.axisY[0].convertPixelToValue(relY)*1000);

    }
    function searchDataPoint() {
        var dps = chart.data[0].dataPoints;
        for(var i = 0; i < dps.length; i++ ) {
            if( (xValue >= dps[i].x - xSnapDistance && xValue <= dps[i].x + xSnapDistance)
            &&(yValue >= dps[i].y*1000 - ySnapDistance && yValue <= dps[i].y*1000 + ySnapDistance)
        ) {
                if(mouseDown) {
                    selected = i;
                    break;
                }
                else {
                    changeCursor = true;
                    break;
                }
            } else {
                selected = null;
                changeCursor = false;
            }
        }
    }
    jQuery("#chartContainer > .canvasjs-chart-container").on({
        mousedown: function(e) {
            mouseDown = true;
            getPosition(e);
            searchDataPoint();
        },
        mousemove: function(e) {
            getPosition(e);
            if(mouseDown) {
                clearTimeout(timerId);
                timerId = setTimeout(function(){
                    if(selected != null) {
                        var color = getColor(yValue/1000.0, threshold);
                        dataPoints[selected].y = yValue/1000.0;
                        dataPoints[selected].color = color;
                        chart.render();
                    }
                }, 0);
            }
            else {
                searchDataPoint();
                if(changeCursor) {
                    chart.data[0].set("cursor", "n-resize");
                } else {
                    chart.data[0].set("cursor", "default");
                }
            }
        },
        mouseup: function(e) {
            if(selected != null) {
                var color = getColor(yValue/1000.0, threshold);
                // chart.data[0].dataPoints[selected].y = yValue/1000.0;
                // chart.data[0].dataPoints[selected].color = color;
                dataPoints[selected].y = yValue/1000.0;
                dataPoints[selected].color = color;
                chart.render();
                mouseDown = false;
            }
        }
    });
}

$(document).on("click", "#hide_explain", function(e) {
    $(".explain").hide();
});

$(document).on("click", "#hide_plot", function(e) {
    // var canvas = $('#chartContainer');
    // // context.clearRect(0, 0, context.width, context.height);
    // const ctx = canvas[0].getContext('2d');
    // ctx.clearRect(0, 0, canvas.width, canvas.height);
    $(".plot").hide();
});

$(document).on("click", "#save_plot", function(e) {
    console.log(dataPoints);
    $.ajax({
		url: "../update",
		type: "POST",
        data: { dataPoints: JSON.stringify(dataPoints)},
        dataType: "json",
        async: true,
        cache: false,
        success: function(data) {
            alert("model updated!");
            // drawAdjustableBar(sorted_data);
		},
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url))
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	    }
	})
});
