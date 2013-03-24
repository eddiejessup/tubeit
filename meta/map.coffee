# set up the lines on the map

picadilly = [ { "x": .05,  "y": .05, "text":'Leicster Square'},  
		  { "x": .20,  "y": .20, "text":'Kings Cross'},
          { "x": .80,  "y": .05, "text":'Euston'},  
		  { "x": .95,  "y": .60, "text":'Covent Garden'}];
			
central = [ { "x": .05,  "y": .05, "text":'Leicster'}, 
          { "x": .40,  "y": .10, "text":'Morningside'},  
          { "x": .60,  "y": .40, "text":'Pall Mall'},  
		  { "x": .95, "y": .60, "text":'Covent Garden'}];

lines = []
lines[0] = picadilly
lines[1] = central

colours = ['teal', 'red']

# set up the svg renderer

svg_width = 2000
svg_height = 2000

offset = 0.02*2000

svg = d3.select("#tube-map")
		.append("svg")
		.attr("width", svg_width)
		.attr("height", svg_height)

_mergeData = (lines) ->
	
	final_array = []
	for line in lines
		Array::push.apply final_array, line
		
	return final_array

# draw the circles
_drawCircles  = (lineData, SVG) ->
	
	circles = SVG.selectAll("circle")
	    .data(lineData)
	    .enter()
	    .append("circle")
	    .style("fill", "white")
	    .style("stroke", "black")
	    .style("stroke-width", 5)

	circleAttributes = circles
	    .attr("cx",  (d) -> (d.x * svg_width))
	    .attr("cy",  (d) -> (d.y * svg_height))
	    .attr("r",  5)
	
	
	text = SVG.selectAll('text')
		.data(lineData)
		.enter()
		.append('text')
		.style('font-family', 'sans-serif')
		.style('font-size', 25)
		.style('fill' , 'gray')
		
	textAttributes = text
	    .attr("x",  (d) -> (d.x * svg_width + offset))
	    .attr("y",  (d) -> (d.y * svg_height+ offset))
		.text((d) -> (d.text))
		
	

# the draw line function
_drawLine = (lineData, colour, SVG) ->

	lineFunction = d3.svg.line()
	                  .x((d) -> d.x * svg_width)
	                  .y((d) -> d.y * svg_height)
	                  .interpolate("cardinal")

	lineGraph = SVG.append("path")
		.attr("d", lineFunction(lineData))
		.attr("stroke", colour)
		.attr("stroke-width", 8)
		.attr("fill", "none")
	    .attr("fill", "none")
		.attr('opacity', '0.5')
							
	totalLength = lineGraph.node().getTotalLength()

	lineGraph
	  .attr("stroke-dasharray", totalLength + " " + totalLength)
	  .attr("stroke-dashoffset", totalLength)
	  .transition()
	    .duration(5000)
	    .ease("linear")
	    .attr("stroke-dashoffset", 0)
	
# run the draw circle function
allData = _mergeData(lines)
_drawCircles(allData, svg)
# run the draw line function	
_drawLine(line, colours[i], svg) for line, i in lines










