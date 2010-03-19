from replay import _ZERO_PROPERTIES, _STAT_WEAPONS
from utils import Toggler

def _player_overview(player):
	odd = Toggler("even", "odd")
	html = '<table class="overview">'
	html += '<tr class="%s"><th>Overall Kills</th><td>%d</td></tr>' % (odd, player.kill_count)
	html += '<tr class="%s"><th>Overall Deaths</th><td>%d</td></tr>' % (odd, player.death_count)
	html += '<tr class="%s"><th>Overall Caps</th><td>%d</td></tr>' % (odd, player.flag_caps)
	html += '</table>'
	return html

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
	%s
</body>
</html>
"""
def player_profile(player):
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
	return _HTML % (player.nick, player.nick, html)
