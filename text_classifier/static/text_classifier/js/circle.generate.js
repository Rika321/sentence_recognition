// function Circles() {}
// var acc =  {{ train_acc }};
var train_acc = parseInt(document.getElementById("train_acc").value*100);
var F1Score = parseInt(document.getElementById("F1Score").value*100);
var total_sample = parseInt(document.getElementById("total_sample").value);
console.log("acc",train_acc);
console.log("f1", F1Score);


var myCircle1 = Circles.create({
  id:                  'circles_ts',
  radius:              60,
  value:               total_sample,
  maxValue:            10000,
  width:               10,
  text:                function(value){return value + '%';},
  colors:              ['#F39C12', '#F1C40F'],
  duration:            400,
  wrpClass:            'circles-wrp',
  textClass:           'circles-text',
  valueStrokeClass:    'circles-valueStroke',
  maxValueStrokeClass: 'circles-maxValueStroke',
  styleWrapper:        true,
  styleText:           true
});
var myCircle2 = Circles.create({
  id:                  'circles_acc',
  radius:              60,
  value:               train_acc,
  maxValue:            100,
  width:               10,
  text:                function(value){return value + '%';},
  colors:              ['#F9E79F', '#D4AC0D'],
  duration:            1600,
  wrpClass:            'circles-wrp',
  textClass:           'circles-text',
  valueStrokeClass:    'circles-valueStroke',
  maxValueStrokeClass: 'circles-maxValueStroke',
  styleWrapper:        true,
  
  styleText:           true
});
var myCircle3 = Circles.create({
  id:                  'circles_f1',
  radius:              60,
  value:               F1Score,
  maxValue:            100,
  width:               10,
  text:                function(value){return value + '%';},
  colors:              ['#D2B4DE', '#7D3C98'],
  duration:            1600,
  wrpClass:            'circles-wrp',
  textClass:           'circles-text',
  valueStrokeClass:    'circles-valueStroke',
  maxValueStrokeClass: 'circles-maxValueStroke',
  styleWrapper:        true,
  styleText:           true
});
var myCircle4 = Circles.create({
  id:                  'circles-4',
  radius:              60,
  value:               43,
  maxValue:            100,
  width:               10,
  text:                function(value){return value + '%';},
  colors:              ['#D3B6C6', '#4B253A'],
  duration:            400,
  wrpClass:            'circles-wrp',
  textClass:           'circles-text',
  valueStrokeClass:    'circles-valueStroke',
  maxValueStrokeClass: 'circles-maxValueStroke',
  styleWrapper:        true,
  styleText:           true
});
