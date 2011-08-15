from replay import _ZERO_PROPERTIES
from report import _WEAPON_NAMES, _WEAPONS
from nicklog import load_timelines
from utils import Toggler, googlechart_url

import os
from math import log

_LOG_SUM_PROPERTIES = _ZERO_PROPERTIES[:]
_LOG_MAX_PROPERTIES = "kill_streak death_streak cap_streak chat_length".split(" ")
for p in _LOG_MAX_PROPERTIES:
	_LOG_SUM_PROPERTIES.remove(p)

def _player_overview(player):
	odd = Toggler("even", "odd")
	html = "<h2>Totals</h2>"
	html += '<table class="overview">'
	html += '<tr class="%s"><th>Frags</th><td>%d</td></tr>\n' % (odd, player.kill_count)
	html += '<tr class="%s"><th>Deaths</th><td>%d</td></tr>\n' % (odd, player.death_count)
	html += '<tr class="%s"><th>Caps</th><td>%d</td></tr>\n' % (odd, player.flag_caps)
	html += '<tr class="%s"><th>Suicides</th><td>%d</td></tr>\n' % (odd, player.suicides)
	html += '<tr class="%s"><th>Team Kills</th><td>%d</td></tr>\n' % (odd, player.team_kills)
	html += '<tr class="%s"><th>Health</th><td>%d</td></tr>\n' % (odd, player.health)
	html += '<tr class="%s"><th>Armor</th><td>%d</td></tr>\n' % (odd, player.armor)
	html += '<tr class="%s"><th>Best Frag Streak</th><td>%d</td></tr>\n' % (odd, player.kill_streak)
	html += '<tr class="%s"><th>Worst Death Streak</th><td>%d</td></tr>\n' % (odd, player.death_streak)
	html += '<tr class="%s"><th>Best Cap Streak</th><td>%d</td></tr>\n' % (odd, player.cap_streak)
	html += '</table>\n'
	return html

def to_level(base, value):
	return int(log(2+(float(value)/base)))

def _player_levels(player):
	odd = Toggler("even", "odd")
	html = "<h2>Levels</h2>"
	html += '<table class="levels">'
	html += '<tr class="%s"><th>Fragger</th><td>Level %d</td></tr>\n' %\
					(odd, to_level(2, player.kill_count))
	html += '<tr class="%s"><th>Capper</th><td>Level %d</td></tr>\n' %\
					(odd, to_level(0.7, player.flag_caps))
	html += '<tr class="%s"><th>Scorer</th><td>Level %d</td></tr>\n' %\
					(odd, to_level(3, player.score))
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
			if j > i+1: # multiple trailing zeros
				j -= 1
				row[j] = row[i-1]
			else: # just one trailing zero
				row[j-1] = row[i-1]
				break
		if i == 0: # edge case: started with zeros
			row[i-1] = row[j]
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
		for weapon,x,y in _WEAPONS:
			wdata = getattr(p, weapon, {}) 
			datapoint.append(wdata.get('hitrate', 0))
		data.append(datapoint)
	data = map(list, zip(*data))
	avg_data = [_average_weapon_row(lst[:]) for lst in data]
	return data, avg_data

def _stat_development(player_timeline):
	html = "<h2>Stat Development</h2>\n"
	data = [
		[p.kill_count for p in player_timeline],
		[p.death_count for p in player_timeline],
		[p.flag_caps *10 for p in player_timeline]]
	url = googlechart_url(data=data, legend=['frags','deaths','caps*10'])
	html += '<img src="%s" />\n' % url
	return html

def merge(player_into, player_from):
	for key in _LOG_SUM_PROPERTIES:
		val = getattr(player_from, key)
		val_old = getattr(player_into, key)
		setattr(player_into, key, val + val_old)
	for key in _LOG_MAX_PROPERTIES:
		val = getattr(player_from, key)
		val_old = getattr(player_into, key)
		setattr(player_into, key, max(val, val_old))
	for w,x,y in _WEAPONS:
		wstats = getattr(player_into, w)
		for attr in ['shots', 'hits', 'kills', 'deaths']:
			wstats[attr] = getattr(player_from, w)[attr]
	return player_into

class Player:
	def __init__(self, **inits):
		for a,v in inits.items():
			setattr(self, a, v)
		for a in _ZERO_PROPERTIES:
			setattr(self, a, 0)
		for w,x,y in _WEAPONS:
			setattr(self, w, {})

_ODD_CLASS = {True: 'odd', False: 'even'}
_HTML= """\
<html>
<head>
	<title>%s</title>
	<link rel="stylesheet" type="text/css" href="media/style.css" /
	<style type="text/css">
	tr.odd { background-color: #ddd; }
	th { font-weight: normal; text-align: left; }
	</style>
</head>
<body>
	<p>View <a href="players.html">Overview of all players</a>.</p>
	<h1>%s profile</h1>
	<h2>Hitrate Development</h2>
	<script type="text/javascript" src="media/protovis-3.1/protovis-d3.1.js"></script>
	<script type="text/javascript" src="media/hitrate_diagram.js"></script>
	<script type="text/javascript+protovis">
	%s
	draw_hitrate(hitrate_points, hitrate_points_interpolated, weapons);
	</script>
	%s
</body>
</html>
"""
def player_profile(player_timeline):
	last = player_timeline[-1]
	P = Player(nick=last.nick)
	player = reduce(merge, player_timeline, P)
	weapon_list = [_WEAPON_NAMES[w].replace("&nbsp;", " ") for (w,y,z) in _WEAPONS]
	data, avg_data = _hitrate_data(player_timeline)
	data = "var hitrate_points = %s;\n" % (str(data))
	data += "var hitrate_points_interpolated = %s;\n" % (str(avg_data))
	data += "var weapons = %s;\n" % weapon_list
	html = ""
	html += _stat_development(player_timeline)
	html += _player_overview(player)
	html += _player_levels(player)
	html += '\n<table style="font-size: 0.8em; float: right;">'
	odd = False
	for prop in _ZERO_PROPERTIES:
		html += '<tr class="%s"><th>%s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], prop, getattr(player, prop))
		odd = not odd
	for weapon,x,y in _WEAPONS:
		for key, val in getattr(player, weapon).items():
			html += '<tr class="%s"><th>%s %s</th><td>%d</td></tr>\n' % (_ODD_CLASS[odd], weapon, key, val)
	html += "</table>\n"
	return _HTML % (player.nick, player.nick, data, html)

def _player_overview_item(odd, player_timeline):
	current = player_timeline[-1]
	slug_nick = player_timeline[0].slug_nick
	nick = player_timeline[0].nick
	return '<tr class="%s"><td class="elo">%d</td><td><a href="p_%s.html">%s</a></td></tr>\n' %\
			 (odd, current.elo*1000, slug_nick, nick)

def _player_elos(timelines):
	elos = [[int(p.elo*1000) for p in line] for line in timelines]
	max_elo = max(max(row) for row in elos)
	nicks = [p[0].nick for p in timelines]
	url = googlechart_url(data=elos, legend=nicks)
	return '<img src="%s" alt="player ELO ratings" />\n' % url

def _hitrate_comparison(weapon, timelines):
	nicks = list()
	hitrates = list()
	for line in timelines:
		d = [getattr(x, weapon)['hitrate'] for x in line][-30:]
		if sum(d) == 0:
			continue
		_average_weapon_row(d)
		nicks.append( line[0].nick )
		hitrates.append( d )
	url = googlechart_url(data=hitrates, legend=nicks)
	html = '<h3>Hitrate with %s</h3>' % (_WEAPON_NAMES[weapon])
	html += '<img src="%s" alt="hitrates with %s" />' % (url, weapon)
	return html

_OVERVIEW_FILE = "players.html"
_OVERVIEW_HTML= """\
<html>
<head>
	<title>Player Overview</title>
	<link rel="stylesheet" type="text/css" href="media/style.css" /
</head>
<body>
	<h1>Player Overview</h1>
	%s
</body>
</html>
"""
def player_overview(timelines, fname):
	def cmp_timeline(t1, t2):
		return -cmp(t1[-1].elo, t2[-1].elo)
	timelines.sort(cmp=cmp_timeline)
	html = ""
	html += '<h2>Elo Development</h2>'
	html += _player_elos(timelines)
	html += '<h2>Elo Ranking</h2>'
	html += '<table class="ranking">\n'
	html += '<tr><th>Elo</th><th>Player</th>\n'
	odd = Toggler("even", "odd")
	for player_timeline in timelines:
		html += _player_overview_item(odd, player_timeline)
	html += '</table>\n'
	for weapon,x,y in _WEAPONS:
		if weapon in ('gauntlet', 'bfg', 'teleport'):
			continue
		html += _hitrate_comparison(weapon, timelines)
	fh = open(fname, 'w')
	fh.write(_OVERVIEW_HTML % html)
	fh.close()

def write_profiles(options):
	timelines = load_timelines(options.nicklog)
	for player_timeline in timelines:
		fname = os.path.join(options.directory, "p_"+player_timeline[0].slug_nick+".html")
		pfh = open(fname, 'w')
		pfh.write(player_profile(player_timeline))
		pfh.close()
	fname = os.path.join(options.directory, _OVERVIEW_FILE)
	player_overview(timelines, fname)
