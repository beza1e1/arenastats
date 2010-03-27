from replay import _ZERO_PROPERTIES, _STAT_WEAPONS
from utils import Toggler

def _player_overview(player):
	odd = Toggler("even", "odd")
	html = '<table class="overview">'
	html += '<tr class="%s"><th>Kills</th><td>%d</td></tr>' % (odd, player.kill_count)
	html += '<tr class="%s"><th>Deaths</th><td>%d</td></tr>' % (odd, player.death_count)
	html += '<tr class="%s"><th>Caps</th><td>%d</td></tr>' % (odd, player.flag_caps)
	html += '<tr class="%s"><th>Suicides</th><td>%d</td></tr>' % (odd, player.suicides)
	html += '<tr class="%s"><th>Team Kills</th><td>%d</td></tr>' % (odd, player.team_kills)
	html += '</table>'
	return html

def _hitrate_data(player_timeline):
	data = []
	for p in player_timeline:
		datapoint = []
		for weapon in _STAT_WEAPONS.values():
			wdata = getattr(p, weapon, {}) 
			datapoint.append(wdata.get('hitrate', 0))
		data.append(datapoint)
	data = map(list, zip(*data))
	return str(data)

def merge(player_into, player_from):
	for key in _ZERO_PROPERTIES:
		val = getattr(player_from, key)
		val_old = getattr(player_into, key)
		setattr(player_into, key, val + val_old)
	for w in _STAT_WEAPONS.values():
		wstats = getattr(player_into, w)
		for attr in ['shots', 'hits', 'kills', 'deaths']:
			wstats[attr] = getattr(player_from, w)[attr]
	return player_into

_ODD_CLASS = {True: 'odd', False: 'even'}
_HTML= """\
<html>
<head>
	<title>%s</title>
	<style>
	tr.odd { background-color: #ddd; }
	th { font-weight: normal; text-align: left; }
	</style>
</head>
<body>
	<h1>%s profile</h1>
	<script type="text/javascript" src="media/protovis-3.1/protovis-d3.1.js"></script>
	<script type="text/javascript+protovis">
	%s
	var vis = new pv.Panel()
		.width(350)
		.height(150);
		
	vis.add(pv.Panel)
		.data(hitrate_data)
		.add(pv.Line)
			.data(function(a) a)
			.bottom(function(d) d * 140)
			.left(function() this.index * 50 + 5)
		.add(pv.Dot)
		.root.render();
	</script>
	%s
</body>
</html>
"""
def player_profile(player_timeline):
	player = reduce(merge, player_timeline)
	data = "var hitrate_data = %s;\n" % _hitrate_data(player_timeline)
	html = ""
	html += _player_overview(player)
	html += '<table style="font-size: 0.8em; float: right;">'
	odd = False
	for prop in _ZERO_PROPERTIES:
		html += '<tr class="%s"><th>%s</th><td>%d</td></tr>' % (_ODD_CLASS[odd], prop, getattr(player, prop))
		odd = not odd
	for weapon in _STAT_WEAPONS.values():
		for key, val in getattr(player, weapon).items():
			html += '<tr class="%s"><th>%s %s</th><td>%d</td></tr>' % (_ODD_CLASS[odd], weapon, key, val)
	html += "</table>\n"
	return _HTML % (player.nick, player.nick, data, html)
