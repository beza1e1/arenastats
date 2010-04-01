from replay import _ZERO_PROPERTIES, _STAT_WEAPONS
from report import _WEAPON_NAMES
from utils import Toggler

def _player_overview(player):
	odd = Toggler("even", "odd")
	html = '<table class="overview">'
	html += '<tr class="%s"><th>Kills</th><td>%d</td></tr>\n' % (odd, player.kill_count)
	html += '<tr class="%s"><th>Deaths</th><td>%d</td></tr>\n' % (odd, player.death_count)
	html += '<tr class="%s"><th>Caps</th><td>%d</td></tr>\n' % (odd, player.flag_caps)
	html += '<tr class="%s"><th>Suicides</th><td>%d</td></tr>\n' % (odd, player.suicides)
	html += '<tr class="%s"><th>Team Kills</th><td>%d</td></tr>\n' % (odd, player.team_kills)
	html += '</table>\n'
	return html

def _average_weapon_row(row):
	"""Interpolate value series by replaceing zeros with average values"""
	i = 0
	while i < len(row):
		if row[i] > 0.0:
			i += 1
			continue
		j = i+1
		while j < len(row): # search end of zero series
			if row[j] > 0.0:
				break
			j += 1
		if j == len(row): # edge case: end reached
			break
		if i == 0: # edge case: started with zeros
			i = j
			continue
		diff = (row[j] - row[i-1]) / (1+j-i)
		plus = row[i-1]
		for k in xrange(i, j):
			plus += diff
			row[k] = plus
		i = j
	return row

def _hitrate_data(player_timeline):
	data = []
	for p in player_timeline:
		datapoint = []
		for weapon in _STAT_WEAPONS.values():
			wdata = getattr(p, weapon, {}) 
			datapoint.append(wdata.get('hitrate', 0))
		data.append(datapoint)
	data = map(list, zip(*data))
	avg_data = [_average_weapon_row(lst[:]) for lst in data]
	return data, avg_data

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
	<script type="text/javascript" src="media/hitrate_diagram.js"></script>
	<script type="text/javascript+protovis">
	%s
	draw_hitrate(hitrate_points, weapons);
	</script>
	%s
</body>
</html>
"""
def player_profile(player_timeline):
	player = reduce(merge, player_timeline)
	weapon_list = _STAT_WEAPONS.values()
	data, avg_data = _hitrate_data(player_timeline)
	data = "var hitrate_points = %s;\n" % (str(data))
	data += "var hitrate_points_interpolated = %s;\n" % (str(avg_data))
	data += "var weapons = %s;\n" % weapon_list
	html = ""
	html += _player_overview(player)
	html += '\n<table style="font-size: 0.8em; float: right;">'
	odd = False
	for prop in _ZERO_PROPERTIES:
		html += '<tr class="%s"><th>%s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], prop, getattr(player, prop))
		odd = not odd
	for weapon in _STAT_WEAPONS.values():
		for key, val in getattr(player, weapon).items():
			html += '<tr class="%s"><th>%s %s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], weapon, key, val)
	html += "</table>\n"
	return _HTML % (player.nick, player.nick, data, html)
