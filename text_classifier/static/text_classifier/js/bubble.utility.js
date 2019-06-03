Array.prototype.contains = function(v) {
    for(var i = 0; i < this.length; i++) {
        if(this[i] === v) return true;
    }
    return false;
};

function getColorByBaiFenBiBubble(bili){
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

function getColorBubble(cluster, radius, len){
    var threshold = 100;
    var contri = radius;
    if(cluster == 1){
        contri = -contri;
    }
    if (contri >= threshold){
        contri = threshold;
    }else if (contri <= -threshold) {
        contri = -threshold;
    }
    contri += threshold;
    var percentage = parseInt(contri/(threshold*2)*100.0);
    if (len == 0){
        //console.log("nega");
        var color = getColorByBaiFenBiBubble(percentage);
    } else {
        //console.log("posi");
        var color = getColorByBaiFenBiBubble(100-percentage);
    }
    return color;
}

function displayBubble(topA_val,topA_name,topB_val,topB_name) {
    // console.log("I am wake!");
    var width = 960,
        height = 500,
        padding = 1.5, // separation between same-color nodes
        clusterPadding = 6, // separation between different-color nodes
        maxRadius = 12;

    var color = d3.scale.ordinal()
        .range(["green","red"]);
          //.range(["#7A99AC", "#E4002B"]);

    // d3.text("word_groups.csv", function(error, text) {
    //   if (error) throw error;
    var colNames = "text,size,group\n";
    // var data = d3.csv.parse(colNames);
    var data = [];
    for (var i = 0; i < topA_name.length; i++) {
        data.push({"text":topA_name[i], "size":topA_val[i]*(-5),"group":"1"})
    }
    for (var i = 0; i < topB_name.length; i++) {
        data.push({"text":topB_name[i], "size":(topB_val[i])*5,"group":"2"})
    }
    console.log(data)

      //var data =   [{"text":"Allagash", "size":"25","group":"1"}, {"text":"Year","size":"20","group":"2"}];
      data.forEach(function(d) {
        d.size = +d.size;
      });

    //

    //unique cluster/group id's
    var cs = [];
    data.forEach(function(d){
            if(!cs.contains(d.group)) {
                cs.push(d.group);
            }
    });

    var n = data.length, // total number of nodes
        m = cs.length; // number of distinct clusters

    //create clusters and nodes
    var clusters = new Array(m);
    var nodes = [];
    for (var i = 0; i<n; i++){
        nodes.push(create_nodes(data,i));
    }

    var force = d3.layout.force()
        .nodes(nodes)
        .size([width, height])
        .gravity(.02)
        .charge(0)
        .on("tick", tick)
        .start();

    var svg = d3.select(".bubble").append("svg")
        .attr("width", width)
        .attr("height", height);


    var node = svg.selectAll("circle")
        .data(nodes)
        .enter().append("g").call(force.drag);

    node.append("circle")
        .style("fill", function (d) {
            return getColorBubble(d.cluster, d.radius, topA_name.length);
        })
        .attr("r", function(d){return d.radius})


    node.append("text")
          .attr("dy", ".3em")
          .style("text-anchor", "middle")
          .text(function(d) { return d.text.substring(0, d.radius / 3); });

  function create_nodes(data,node_counter) {
    var i = cs.indexOf(data[node_counter].group),
        r = Math.sqrt((i + 1) / m * -Math.log(Math.random())) * maxRadius,
        d = {
          cluster: i,
          radius: data[node_counter].size*1.5,
          text: data[node_counter].text,
          x: Math.cos(i / m * 2 * Math.PI) * 200 + width / 2 + Math.random(),
          y: Math.sin(i / m * 2 * Math.PI) * 200 + height / 2 + Math.random()
        };
        // color(d.cluster)
    if (!clusters[i] || (r > clusters[i].radius)) clusters[i] = d;
    return d;
  };


  function tick(e) {
      node.each(cluster(10 * e.alpha * e.alpha))
          .each(collide(.5))
      .attr("transform", function (d) {
          var k = "translate(" + d.x + "," + d.y + ")";
          return k;
      })

  }

  // Move d to be adjacent to the cluster node.
  function cluster(alpha) {
      return function (d) {
          var cluster = clusters[d.cluster];
          if (cluster === d) return;
          var x = d.x - cluster.x,
              y = d.y - cluster.y,
              l = Math.sqrt(x * x + y * y),
              r = d.radius + cluster.radius;
          if (l != r) {
              l = (l - r) / l * alpha;
              d.x -= x *= l;
              d.y -= y *= l;
              cluster.x += x;
              cluster.y += y;
          }
      };
  }

  // Resolves collisions between d and all other circles.
  function collide(alpha) {
      var quadtree = d3.geom.quadtree(nodes);
      return function (d) {
          var r = d.radius + maxRadius + Math.max(padding, clusterPadding),
              nx1 = d.x - r,
              nx2 = d.x + r,
              ny1 = d.y - r,
              ny2 = d.y + r;
          quadtree.visit(function (quad, x1, y1, x2, y2) {
              if (quad.point && (quad.point !== d)) {
                  var x = d.x - quad.point.x,
                      y = d.y - quad.point.y,
                      l = Math.sqrt(x * x + y * y),
                      r = d.radius + quad.point.radius + (d.cluster === quad.point.cluster ? padding : clusterPadding);
                  if (l < r) {
                      l = (l - r) / l * alpha;
                      d.x -= x *= l;
                      d.y -= y *= l;
                      quad.point.x += x;
                      quad.point.y += y;
                  }
              }
              return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
          });
      };
  }

}
