from replay import _ZERO_PROPERTIES, _STAT_WEAPONS

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
	html += "<table>"
	odd = False
	for prop in _ZERO_PROPERTIES:
		html += '<tr class="%s"><th>%s</th><td>%d</td></tr>' % (_ODD_CLASS[odd], prop, getattr(player, prop))
		odd = not odd
	for weapon in _STAT_WEAPONS.values():
		for key, val in getattr(player, weapon).items():
			html += '<tr class="%s"><th>%s %s</th><td>%d</td></tr>' % (_ODD_CLASS[odd], weapon, key, val)
	html += "</table>\n"
	return _HTML % (player.nick, player.nick, html)
