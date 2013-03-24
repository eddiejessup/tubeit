# set up the svg renderer
svg_width = 2000
svg_height = 2000

offset = 0.02*2000

# initiate the liens and colouts data
lines = []
colours = ['teal', 'silver', 'sienna', 'plum', 'orange', 'indigo', 'gold', 'cyan', 'red', 'aqua']

# merge data function for drawing all the circles, need to work out a wat
# to make the curcles draw for each line object individually but thats not
# working atm.
_mergeData = (lines) ->

	final_array = []
	for line in lines
		Array::push.apply final_array, line
	
	return final_array

# draw the circles from the line data onto the SVG
_drawCircles  = (lineData, SVG) ->

	circles = SVG.selectAll("circle")
	    .data(lineData)
	    .enter()
	    .append("circle")
	    .style("fill", "white")
	    .style("stroke", "black")
	    .style("stroke-width", 4)

	circleAttributes = circles
	    .attr("cx",  (d) -> (d.r[0] * svg_width))
	    .attr("cy",  (d) -> (d.r[1] * svg_height))
	    .attr("r",  8)


	text = SVG.selectAll('text')
		.data(lineData)
		.enter()
		.append('text')
		.style('font-family', 'sans-serif')
		.style('font-size', 25)
		.style('fill' , 'gray')
	
	textAttributes = text
	    .attr("x",  (d) -> (d.r[0] * svg_width + offset))
	    .attr("y",  (d) -> (d.r[1] * svg_height+ offset))
		.text((d) -> (d.text))
	


# the draw line function on the the SVG with a given colour
_drawLine = (lineData, colour, SVG) ->

	lineFunction = d3.svg.line()
	                  .x((d) -> d.r[0] * svg_width)
	                  .y((d) -> d.r[1] * svg_height)
	                  .interpolate("cardinal")

	lineGraph = SVG.append("path")
		.attr("d", lineFunction(lineData))
		.attr("stroke", colour)
		.attr("stroke-width", 7)
		.attr("fill", "none")
	    .attr("fill", "none")
		.attr('opacity', '0.9')
		
	totalLength = lineGraph.node().getTotalLength()

	lineGraph
	  .attr("stroke-dasharray", totalLength + " " + totalLength)
	  .attr("stroke-dashoffset", totalLength)
	  .transition()
	    .duration(10000)
	    .ease("linear")
	    .attr("stroke-dashoffset", 0)

svg = d3.select("#tube-map")
		.append("svg")
		.attr("width", svg_width)
		.attr("height", svg_height)
		
# make a json call to the map.jason file stored in this directory
d3.json "http://localhost:8008/map.json", (jsondata) ->
	
	# loop though the values in the json data
	for i, value of jsondata
		lines[i] = value.nodes

		console.log(lines[i])
		console.log(colours)

		# everything from here needs to be indented to make sure it falls within the
		# d3.json call

	# run the draw line function	
	_drawLine(line, colours[i], svg) for line, i in lines
	# run the draw circle function
	allData = _mergeData(lines)
	_drawCircles(allData, svg)










