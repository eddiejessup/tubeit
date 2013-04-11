var main, colours, lines, offset, svg, svg_height, svg_width, _drawCircles, _drawLine, _mergeData;

svg_width = 2000;
svg_height = 2000;
offset = 0.02 * 2000;
lines = [];
colours = ['teal', 'silver', 'sienna', 'plum', 'orange', 'indigo', 'gold', 'cyan', 'red', 'aqua'];

_mergeData = function(lines) {
var final_array, line, _i, _len;
    final_array = [];
    for (_i = 0, _len = lines.length; _i < _len; _i++) {
    line = lines[_i];
      Array.prototype.push.apply(final_array, line);
    }
    return final_array;
};

_drawCircles = function(lineData, SVG) {
    var circleAttributes, circles, text, textAttributes;

    circles = SVG.selectAll("circle").data(lineData).enter().append("circle").style("fill", "white").style("stroke", "black").style("stroke-width", 4);
    circleAttributes = circles.attr("cx", function(d) {
        return d.r[0] * svg_width;
    }).attr("cy", function(d) {
        return d.r[1] * svg_height;
    }).attr("r", 8);
    text = SVG.selectAll('text').data(lineData).enter().append('text').style('font-family', 'sans-serif').style('font-size', 25).style('fill', 'gray');
    return textAttributes = text.attr("x", function(d) {
        return d.r[0] * svg_width + offset;
    }).attr("y", function(d) {
        return d.r[1] * svg_height + offset;
    }).text(function(d) {
        return d.text;
    });
};

_drawLine = function(lineData, colour, SVG) {
    var lineFunction, lineGraph, totalLength;

    lineFunction = d3.svg.line().x(function(d) {
        return d.r[0] * svg_width;
    }).y(function(d) {
        return d.r[1] * svg_height;
    }).interpolate("cardinal");
    lineGraph = SVG.append("path").attr("d", lineFunction(lineData)).attr("stroke", colour).attr("stroke-width", 7).attr("fill", "none").attr("fill", "none").attr('opacity', '0.9');
    totalLength = lineGraph.node().getTotalLength();
    return lineGraph.attr("stroke-dasharray", totalLength + " " + totalLength).attr("stroke-dashoffset", totalLength).transition().duration(10000).ease("linear").attr("stroke-dashoffset", 0);
};

svg = d3.select("#tube-map").append("svg").attr("width", svg_width).attr("height", svg_height);

main = function(jsondata) {
    var allData, i, line, _i, _len;

    for (i in jsondata) {
      lines[i] = jsondata[i].nodes;
      console.log(lines[i]);
    }
    for (i = _i = 0, _len = lines.length; _i < _len; i = ++_i) {
      line = lines[i];
      _drawLine(line, colours[i], svg);
    }
    allData = _mergeData(lines);
    return _drawCircles(allData, svg);
}