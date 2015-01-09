
var width = window.innerWidth;
var height = window.innerHeight;

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-300)
    .linkDistance(120)
    .size([width, height]);

var drawGraph = function(graph, depth) {
  
  // refresh svg layer
  d3.select("svg").remove();
  var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

  // code snippet to add arrow
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

    // Force node to reside in columns
    var widthBand = 0.8*width/depth;
    console.log("tick");
    for(var j = 0; j < node.data().length; j++){
      node.data()[j].x =  widthBand*(node.data()[j].group + 0.2);
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


// Reverse adj from the data from parse
// The reversed list has the finished food as root
// The leaves are ingredients

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

// DFS from roots
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

// not used
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

    // build nodes and egdes (for d3 force laye to accept)
    // build conventional adjList
    nodes = [];
    edges = [];
    adjList = [];

    // regex to obtain the things in "" 
    var lines = $('#inputBox').val().trim().split('\n');
    var thisLine;
    var myRegexp = /\"(.*?)\"/;

    // parse and build
    for(var i = 0;i < lines.length;i++){
        thisLine = lines[i].trim();
        console.log(thisLine);
        var match = myRegexp.exec(thisLine);
        console.log(match);
        var ing = match[1];
        var num = thisLine.split(match[0]);
        var thisNodeNum = num[0];
        var thisChildrenNum = num[1];
        nodes.push({"name": ing, "group": -1});
        var edgesAdjList = []
        if (thisChildrenNum){
          thisChildrenNum = thisChildrenNum.trim();
          var childrenList = thisChildrenNum.split(",");
          for(var j=0; j< childrenList.length; j++){
            edges.push({"source": parseInt(thisNodeNum), "target": parseInt(childrenList[j]) ,"value": 1 });
            edgesAdjList.push(parseInt(childrenList[j]));
          }
        }
        adjList.push(edgesAdjList);
    }

    // graph is object format that works with the lib
    // newAdj is the reverser adjList (roots are finished food)
    // having the original one help to see when things separate
    // roots of this reversed list (finished food, or discarded stuff, mislabeled)

    var graph = {"nodes": nodes, "links": edges};
    var newAdjRoots = reverseAdj(adjList);
    var newAdj = newAdjRoots.adj;
    var roots = newAdjRoots.roots;

    // label distance and change the group of the object
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

    // draw graph

    drawGraph(graph, depth);

  });

}); 
