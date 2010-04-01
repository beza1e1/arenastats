function draw_hitrate(hitrate_points, weapons) {
	/* calculate line data. For 0.0 values use the value of the predecessor */
	var n_weapons = hitrate_points.length;
	var hitrate_lines = Array(n_weapons);
	var visible = Array(n_weapons);
	for (w = 0; w < n_weapons; ++w) {
		var weapon_data = hitrate_points[w];
		var length = weapon_data.length;
		var new_data = Array(length);
		var last = 0.0;
		var allZero = true;
		for (d = 0; d < length; ++d) {
			var datum = weapon_data[d];
			if (datum == 0.0) {
				datum = last;
			} else {
				allZero = false;
			}
			new_data[d] = datum;
			last = weapon_data[d];
		}
		visible[w] = !allZero;
		hitrate_lines[w] = new_data;
	}

	Array.max = function(array) {
		return Math.max.apply(Math, array);
	};

	var datapoints_h = hitrate_points[0].length;

	/* color scale */
	var c = pv.Colors.category20();

	var vis = new pv.Panel()
		.width(100 + datapoints_h * 30)
		.height(150)
		.bottom(20);
		
	vis.add(pv.Panel)
		.left(100)
		.data(hitrate_lines)
		.add(pv.Line)
			.strokeStyle(function(d) c(this.parent.index))
			.data(function(a) a)
			.bottom(function(d) d * 140)
			.left(function() this.index * 30)
			.visible(function() visible[this.parent.index])
		.add(pv.Dot)
			.data(function() hitrate_points[this.parent.index])
			.visible(function(d) d > 0);

	/* Legende */
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
