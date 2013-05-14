svg_width = 0.8 * window.innerWidth
svg_height = 0.7 * window.innerHeight

offset = 0.01

# colours = ['teal', 'silver', 'sienna', 'plum', 'orange', 'indigo', 'gold', 'cyan', 'red', 'aqua', 'black']
colours = ["AliceBlue", "AntiqueWhite", "Aqua", "Aquamarine", "Azure", "Beige", "Bisque", "Black", "BlanchedAlmond", "Blue", "BlueViolet", "Brown", "BurlyWood", "CadetBlue", "Chartreuse", "Chocolate", "Coral", "CornflowerBlue", "Cornsilk", "Crimson", "Cyan", "DarkBlue", "DarkCyan", "DarkGoldenRod", "DarkGray", "DarkGrey", "DarkGreen", "DarkKhaki", "DarkMagenta", "DarkOliveGreen", "Darkorange", "DarkOrchid", "DarkRed", "DarkSalmon", "DarkSeaGreen", "DarkSlateBlue", "DarkSlateGray", "DarkSlateGrey", "DarkTurquoise", "DarkViolet", "DeepPink", "DeepSkyBlue", "DimGray", "DimGrey", "DodgerBlue", "FireBrick", "FloralWhite", "ForestGreen", "Fuchsia", "Gainsboro", "GhostWhite", "Gold", "GoldenRod", "Gray", "Grey", "Green", "GreenYellow", "HoneyDew", "HotPink", "IndianRed", "Indigo", "Ivory", "Khaki", "Lavender", "LavenderBlush", "LawnGreen", "LemonChiffon", "LightBlue", "LightCoral", "LightCyan", "LightGoldenRodYellow", "LightGray", "LightGrey", "LightGreen", "LightPink", "LightSalmon", "LightSeaGreen", "LightSkyBlue", "LightSlateGray", "LightSlateGrey", "LightSteelBlue", "LightYellow", "Lime", "LimeGreen", "Linen", "Magenta", "Maroon", "MediumAquaMarine", "MediumBlue", "MediumOrchid", "MediumPurple", "MediumSeaGreen", "MediumSlateBlue", "MediumSpringGreen", "MediumTurquoise", "MediumVioletRed", "MidnightBlue", "MintCream", "MistyRose", "Moccasin", "NavajoWhite", "Navy", "OldLace", "Olive", "OliveDrab", "Orange", "OrangeRed", "Orchid", "PaleGoldenRod", "PaleGreen", "PaleTurquoise", "PaleVioletRed", "PapayaWhip", "PeachPuff", "Peru", "Pink", "Plum", "PowderBlue", "Purple", "Red", "RosyBrown", "RoyalBlue", "SaddleBrown", "Salmon", "SandyBrown", "SeaGreen", "SeaShell", "Sienna", "Silver", "SkyBlue", "SlateBlue", "SlateGray", "SlateGrey", "Snow", "SpringGreen", "SteelBlue", "Tan", "Teal", "Thistle", "Tomato", "Turquoise", "Violet", "Wheat", "White", "WhiteSmoke", "Yellow", "YellowGreen"];

_drawCircles = (nodes, SVG) ->

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

_drawLine = (nodes, path, colour, SVG, animate) ->

	lineFunction = d3.svg.line()
	                  .x((d) -> nodes[d].x * svg_width)
	                  .y((d) -> nodes[d].y * svg_height)
	                  .interpolate("linear")

	lineGraph = SVG.append("path")
		.attr("d", lineFunction(path.nodes))
		.attr("stroke", colour)
		.attr("stroke-width", 5)
		.attr("fill", "none")
	    .attr("fill", "none")
		.attr('opacity', '0.6')

	if animate
		totalLength = lineGraph.node().getTotalLength()

		lineGraph
		  .attr("stroke-dasharray", totalLength + " " + totalLength)
		  .attr("stroke-dashoffset", totalLength)
		  .transition()
		    .duration(10000)
		    .ease("linear")
		    .attr("stroke-dashoffset", 0)
	else
		totalLength = lineGraph.node().getTotalLength()

		lineGraph
		  .attr("stroke-dasharray", totalLength + " " + totalLength)
		  .attr("stroke-dashoffset", totalLength)
		  .transition()
		    .duration(0)
		    .ease("linear")
		    .attr("stroke-dashoffset", 0)

main = (data, animate) ->

	svg = d3.select(".span12")
			.append("svg")
			.attr("width", svg_width)
			.attr("height", svg_height)

	for node, i in data.nodes
		node.x -= 0.5
		node.x *= 0.95
		node.x += 0.5

		node.y -= 0.5
		node.y *= 0.95
		node.y += 0.5

	_drawCircles(data.nodes, svg)
	_drawLine(data.nodes, path, colours[i], svg, animate) for path, i in data.paths