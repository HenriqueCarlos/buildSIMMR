// var adjList = "[10]
// [10]
// [11]
// [12]
// [12]
// [13]
// [13]
// [13]
// [13]
// [18]
// [11]
// [12]
// [13]
// [14, 15]
// [16, 17]
// [18]
// [19]
// []
// [19]
// []";


var width = window.innerWidth;
var height = window.innerHeight;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-300)
    .linkDistance(120)
    .size([width, height]);






var drawGraph = function(graph, depth) {

  var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

  svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
  .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");
  //http://bl.ocks.org/d3noob/5141278

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .attr("marker-end", "url(#end)")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var gnodes = svg.selectAll('g.gnode')
     .data(graph.nodes)
     .enter()
     .append('g')
     .classed('gnode', true);
    
  var node = gnodes.append("circle")
      .attr("class", "node")
      .attr("r", 5)
      .style("fill", function(d) { return color(d.group); })
      .call(force.drag);

  var labels = gnodes.append("text")
      .text(function(d) { return d.name; });



  force.on("tick", function(e) {

    //     .attr("cy", function(d) { return d.y; });
    var widthBand = 0.8*width/depth;

    var ky = .1 * e.alpha, kx = .1* e.alpha;
    // Push nodes toward their designated focus.
    console.log("tick");
    for(var j = 0; j < node.data().length; j++){
      // console.log(node.data()[j]);
      node.data()[j].x =  widthBand*(node.data()[j].group + 0.2);
      // link.data()[j].source.y += (link.data()[j].target.y -  link.data()[j].source.y) * ky;
    }

    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    gnodes.attr("transform", function(d) { 
        return 'translate(' + [d.x, d.y] + ')'; 
    });
      
    
      
  });
};

// drawGraph(graph);



function reverseAdj(adjList){
  var numNodes = adjList.length;
  newAdj = [];
  checkRoot = [];
  for (var i = 0; i< numNodes; i++) {
    newAdj.push([]);
    checkRoot.push(0);
  }

  for (var i = 0; i < adjList.length; i++) {
    for (var j = 0; j< adjList[i].length; j++){
      newAdj[adjList[i][j]].push(i);
      checkRoot[i] = 1;
    }
  }

  var roots = [];
  for (var i = 0; i < checkRoot.length; i++) {
    if (checkRoot[i] == 0){
      roots.push(i);
    }
  };
  return {"adj":newAdj, "roots": roots};
}

function labelLength(rootIndex, adjListRe, nodes ){
  console.log("this root"+rootIndex);
  var edgesFromThisNode = adjListRe[rootIndex];
  nodes[rootIndex].group++;
  console.log(edgesFromThisNode);
  for (var i = 0; i < edgesFromThisNode.length; i++) {
    // do some work
    if ((nodes[rootIndex].group > nodes[edgesFromThisNode[i]].group)){
      nodes[edgesFromThisNode[i]].group = nodes[rootIndex].group;
      labelLength(edgesFromThisNode[i], adjListRe, nodes);
    }

  };

}

function labelSibSeparate(nodes, adjList){
  for (var i = 0; i < adjList.length; i++) {
    if (adjList[i].length > 1){
      var minGroup = 100000;
      for( var j = 0; j< adjList[i].length; j++){
        if (nodes[adjList[i][j]].group != 1) minGroup = Math.min(minGroup, nodes[adjList[i][j]].group);
      };
      for (var j = 0; j < adjList[i].length; j++) {
        nodes[adjList[i][j]].group = minGroup;
      };
    }
  };
}

$(document).ready(function(){

  $("#submitButton").click(function (e) {

    d3.select("svg").remove();
      
    var lines = $('#inputBox').val().trim().split('\n');
    var thisLine;
    var myRegexp = /^\d+\s+\"(.*?)\"/;
    nodes = [];
    edges = [];
    adjList = [];
    for(var i = 0;i < lines.length;i++){
        thisLine = lines[i].trim();
        // console.log("new:" +thisLine);
        var match = myRegexp.exec(thisLine);
        var ing = match[1];
        var num = thisLine.split(('\"'+ing+'\"'));
        var thisNodeNum = num[0];
        var thisChildrenNum = num[1];
        nodes.push({"name": ing, "group": -1});
        // console.log(ing);
        var edgesAdjList = []
        if (thisChildrenNum){
          thisChildrenNum = thisChildrenNum.trim();
          var childrenList = thisChildrenNum.split(",");
          for(var j=0; j< childrenList.length; j++){
            edges.push({"source": parseInt(thisNodeNum), "target": parseInt(childrenList[j]) ,"value": 1 });
            edgesAdjList.push(parseInt(childrenList[j]));
          }
        }
        else{
          // console.log("no children");
        }
        adjList.push(edgesAdjList);
    }
    var graph = {"nodes": nodes, "links": edges};
    var newAdjRoots = reverseAdj(adjList);
    var newAdj = newAdjRoots.adj;
    var roots = newAdjRoots.roots;

    // label distance
    console.log("roots");
    for (var i = 0; i < roots.length; i++) {
      console.log(nodes[roots[i]].name);
      labelLength(roots[i], newAdj, nodes);
    };

    // labelSibSeparate(nodes,adjList);
    // finding height of the dag
    var depth = -1;
    for (var i = 0; i < nodes.length; i++) {
      if (depth < nodes[i].group) depth = nodes[i].group;
    };

    drawGraph(graph, depth);

  });

}); 
