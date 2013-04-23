svg_width = window.innerWidth
svg_height = window.innerHeight

offset = 0.01

colours = ['teal', 'silver', 'sienna', 'plum', 'orange', 'indigo', 'gold', 'cyan', 'red', 'aqua']

_drawCircles = (nodes, SVG) ->

	console.log(nodes)
	circles = SVG.selectAll("circle")
	    .data(nodes)
	    .enter()
	    .append("circle")
	    .style("fill", "white")
	    .style("stroke", "black")
	    .style("stroke-width", 4)

	circleAttributes = circles
	    .attr("cx", (d) -> (d.x * svg_width))
	    .attr("cy", (d) -> (d.y * svg_height))
	    .attr("r", 7)

	text = SVG.selectAll('text')
		.data(nodes)
		.enter()
		.append('text')
		.style('font-family', 'sans-serif')
		.style('font-size', 16)
		.style('fill' , 'gray')

	textAttributes = text
	    .attr("x", (d) -> ((d.x + offset) * svg_width))
	    .attr("y", (d) -> ((d.y + offset) * svg_height))
		.text((d) -> (d.label))

_drawLine = (nodes, path, colour, SVG) ->

	lineFunction = d3.svg.line()
	                  .x((d) -> nodes[d].x * svg_width)
	                  .y((d) -> nodes[d].y * svg_height)
	                  .interpolate("cardinal")

	lineGraph = SVG.append("path")
		.attr("d", lineFunction(path.nodes))
		.attr("stroke", colour)
		.attr("stroke-width", 5)
		.attr("fill", "none")
	    .attr("fill", "none")
		.attr('opacity', '0.6')

	totalLength = lineGraph.node().getTotalLength()

	lineGraph
	  .attr("stroke-dasharray", totalLength + " " + totalLength)
	  .attr("stroke-dashoffset", totalLength)
	  .transition()
	    .duration(10000)
	    .ease("linear")
	    .attr("stroke-dashoffset", 0)

main = (data) ->

	svg = d3.select("#tube-map")
			.append("svg")
			.attr("width", svg_width)
			.attr("height", svg_height)

	_drawCircles(data.nodes, svg)
	_drawLine(data.nodes, path, colours[i], svg) for path, i in data.paths