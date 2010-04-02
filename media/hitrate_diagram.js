draw_hitrate = function(hitrate_points, hitrate_lines, weapons) {
	/* calculate line data. For 0.0 values use the value of the predecessor */
	var n_weapons = hitrate_points.length;
	var visible = Array(n_weapons);
	for (w = 0; w < n_weapons; ++w) {
		var data = hitrate_points[w];
		var allZero = true;
		for (d = 0; d < data.length; ++d) {
			if (data[d] > 0.0) {
				allZero = false;
			}
		}
		visible[w] = !allZero;
	}

	var datapoints_h = hitrate_points[0].length;
	var diagram_width = 600;
	var point_gap = diagram_width / datapoints_h;

	/* color scale */
	var c = pv.colors(
		"#3cf", // gauntlet
		"#ff0", // machine gun
		"orange", // shotgun
		"#e00", // rocket launcher
		"#c09", // plasma gun
		"#390", // grenade launcher
		"#cc3", // lighning gun
		"#5d0", // railgun
		"#0ff", // bfg
		"black" // teleport
	);

	var vis = new pv.Panel()
		.width(diagram_width + 120) // plus legend
		.height(150)
		.bottom(20);
		
	vis.add(pv.Panel)
		.left(110)
		.data(hitrate_lines)
		.add(pv.Line)
			.strokeStyle(function() c(this.parent.index))
			.data(function(d) d)
			.bottom(function(d) d * 140)
			.left(function() this.index * point_gap)
		.add(pv.Dot)
			.data(function() hitrate_points[this.parent.index])
			.visible(function(d) d > 0);

	/* Legend */
	legende = vis.add(pv.Panel);

	legende.add(pv.Dot)
		.data(weapons)
		.left(10)
		.top(function() this.index * 12 + 10)
		.strokeStyle(null)
		.fillStyle(function(d) visible[this.index] ? c(this.index) : "#BBBBBB")
	.anchor("right").add(pv.Label)
		.text(function(d) d)
		.textStyle(function(d) visible[this.index] ? "black" : "#BBBBBB");

	vis.render();
}
