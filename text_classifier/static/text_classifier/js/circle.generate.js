// function Circles() {}
// var acc =  {{ train_acc }};
var train_acc = parseInt(document.getElementById("train_acc").value*100);
var F1Score = parseInt(document.getElementById("F1Score").value*100);
var total_sample = parseInt(document.getElementById("total_sample").value);


var myCircle1 = Circles.create({
  id:                  'circles-1',
  radius:              60,
  value:               total_sample,
  maxValue:            10000,
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
var myCircle2 = Circles.create({
  id:                  'circles-2',
  radius:              60,
  value:               train_acc,
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
var myCircle3 = Circles.create({
  id:                  'circles-3',
  radius:              60,
  value:               F1Score,
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
// Example 1
//function(currentValue) {/
//  return '$'+currentValue;
//};
// // Example 2
// function() {
//   return this.getPercent() + '%';
// }
//
// myCircle.updateRadius(Number 100)
// myCircle.updateWidth(Number width)
// myCircle.updateColors(Array colors)
// myCircle.update(Boolean force)
// myCircle.getPercent()
// myCircle.getValue()
// myCircle.getMaxValue()
// myCircle.getValueFromPercent(Number percentage)
// myCircle.htmlifyNumber(Number number[, integerPartClass, decimalPartClass])
// myCircle.update(Number value [, Number duration])
