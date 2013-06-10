// Generated by CoffeeScript 1.4.0
var colours, main, offset, svg_height, svg_width, _drawCircles, _drawLine;

svg_width = 400;

svg_height = 400;

offset = 0.01;

colours = ["AliceBlue", "Aqua", "Aquamarine", "Azure", "Beige", "Bisque", "BlanchedAlmond", "Blue", "BlueViolet", "Brown", "BurlyWood", "CadetBlue", "Chartreuse", "Chocolate", "Coral", "CornflowerBlue", "Cornsilk", "Crimson", "Cyan", "DarkBlue", "DarkCyan", "DarkGoldenRod", "DarkGray", "DarkGrey", "DarkGreen", "DarkKhaki", "DarkMagenta", "DarkOliveGreen", "Darkorange", "DarkOrchid", "DarkRed", "DarkSalmon", "DarkSeaGreen", "DarkSlateBlue", "DarkSlateGray", "DarkSlateGrey", "DarkTurquoise", "DarkViolet", "DeepPink", "DeepSkyBlue", "DimGray", "DimGrey", "DodgerBlue", "FireBrick", "FloralWhite", "ForestGreen", "Fuchsia", "Gainsboro", "GhostWhite", "Gold", "GoldenRod", "Gray", "Grey", "Green", "GreenYellow", "HoneyDew", "HotPink", "IndianRed", "Indigo", "Ivory", "Khaki", "Lavender", "LavenderBlush", "LawnGreen", "LemonChiffon", "LightBlue", "LightCoral", "LightCyan", "LightGoldenRodYellow", "LightGray", "LightGrey", "LightGreen", "LightPink", "LightSalmon", "LightSeaGreen", "LightSkyBlue", "LightSlateGray", "LightSlateGrey", "LightSteelBlue", "LightYellow", "Lime", "LimeGreen", "Linen", "Magenta", "Maroon", "MediumAquaMarine", "MediumBlue", "MediumOrchid", "MediumPurple", "MediumSeaGreen", "MediumSlateBlue", "MediumSpringGreen", "MediumTurquoise", "MediumVioletRed", "MidnightBlue", "MintCream", "MistyRose", "Moccasin", "NavajoWhite", "Navy", "OldLace", "Olive", "OliveDrab", "Orange", "OrangeRed", "Orchid", "PaleGoldenRod", "PaleGreen", "PaleTurquoise", "PaleVioletRed", "PapayaWhip", "PeachPuff", "Peru", "Pink", "Plum", "PowderBlue", "Purple", "Red", "RosyBrown", "RoyalBlue", "SaddleBrown", "Salmon", "SandyBrown", "SeaGreen", "SeaShell", "Sienna", "Silver", "SkyBlue", "SlateBlue", "SlateGray", "SlateGrey", "Snow", "SpringGreen", "SteelBlue", "Tan", "Teal", "Tomato", "Turquoise", "Violet", "Yellow", "YellowGreen"];

_drawCircles = function(nodes, SVG) {
  var circleAttributes, circles, text, textAttributes;
  circles = SVG.selectAll("circle").data(nodes).enter().append("circle").style("fill", "white").style("stroke", "black").style("stroke-width", 4);
  circleAttributes = circles.attr("cx", function(d) {
    return d.x * svg_width;
  }).attr("cy", function(d) {
    return d.y * svg_height;
  }).attr("r", 7);
  text = SVG.selectAll('text').data(nodes).enter().append('text').style('font-family', 'sans-serif').style('font-size', 16).style('fill', 'gray');
  return textAttributes = text.attr("x", function(d) {
    return (d.x + offset) * svg_width;
  }).attr("y", function(d) {
    return (d.y + offset) * svg_height;
  }).text(function(d) {
    return d.label;
  });
};

_drawLine = function(nodes, path, SVG, animate) {
  var lineFunction, lineGraph, totalLength;
  lineFunction = d3.svg.line().x(function(d) {
    return nodes[d].x * svg_width;
  }).y(function(d) {
    return nodes[d].y * svg_height;
  }).interpolate("linear");
  lineGraph = SVG.append("path").attr("d", lineFunction(path.nodes)).attr("stroke", colours[Math.floor(Math.random() * colours.length)]).attr("stroke-width", 5).attr("fill", "none").attr("fill", "none").attr('opacity', '0.6');
  if (animate) {
    totalLength = lineGraph.node().getTotalLength();
    return lineGraph.attr("stroke-dasharray", totalLength + " " + totalLength).attr("stroke-dashoffset", totalLength).transition().duration(10000).ease("linear").attr("stroke-dashoffset", 0);
  } else {
    totalLength = lineGraph.node().getTotalLength();
    return lineGraph.attr("stroke-dasharray", totalLength + " " + totalLength).attr("stroke-dashoffset", totalLength).transition().duration(0).ease("linear").attr("stroke-dashoffset", 0);
  }
};

main = function(data, animate) {
  var i, node, path, svg, _i, _j, _len, _len1, _ref, _ref1, _results;
  svg = d3.select(".span12").append("svg").attr("width", svg_width).attr("height", svg_height);
  _ref = data.nodes;
  for (i = _i = 0, _len = _ref.length; _i < _len; i = ++_i) {
    node = _ref[i];
    node.x -= 0.5;
    node.x *= 0.95;
    node.x += 0.5;
    node.y -= 0.5;
    node.y *= 0.95;
    node.y += 0.5;
  }
  _drawCircles(data.nodes, svg);
  _ref1 = data.paths;
  _results = [];
  for (i = _j = 0, _len1 = _ref1.length; _j < _len1; i = ++_j) {
    path = _ref1[i];
    _results.push(_drawLine(data.nodes, path, svg, animate));
  }
  return _results;
};
