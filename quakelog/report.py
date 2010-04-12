# -!- encoding: utf-8 -!-
import os
from utils import Toggler, infinity

def gen_player_links(players, team_id):
	ps = list()
	for p in players:
		if hasattr(p, 'team_id') and p.team_id == team_id:
			ps.append('<a href="#%s">%s</a>' % (p.slug_nick, p.nick))
	return ", ".join(ps)

def pluralize(number, unit, emph_bound=0):
	if 1 == number:
		return "%d %s" % (number, unit)
	else: # plural
		if emph_bound > 0 and number > emph_bound:
			return "<strong>%d %ss</strong>" % (number, unit)
		else:
			return "%d %ss" % (number, unit)

def general_game_info(game, levelshots):
	html = '<div class="game_stats"\n'
	html += '<img src="%s/%s.jpg" />' % (levelshots, game.mapname)
	html += '<table class="game_info">\n'
	html += "<tr><td>Map</td><td>%s</td></tr>\n" % (game.mapname)
	html += "<tr><td>Date</td><td>%s</td></tr>\n" % (game.datetime)
	html += "<tr><td>Game type</td><td>%s</td></tr>\n" % (game.gametype)
	html += '<tr><td>Total Frags</td><td><a href="#kill_matrix">%d</a></td></tr>\n' % (game.frag_count)
	html += "</table>\n"
	if not 1 in game.teams:
		print "Not a CTF game!" # TODO
		return html
	html += '<table>\n<tr class="game_result">\n'
	html += '<td class="team_red">%s</td>' % game.teams[1].capture_count
	html += "<td>vs</td>"
	html += '<td class="team_blue">%s</td>' % game.teams[2].capture_count
	html += "</tr><tr>"
	players = game.sortedPlayers()
	html += '<td>%s</td><td> </td><td>%s</td>' % (gen_player_links(players, 1), gen_player_links(players, 2))
	html += "</tr>\n</table>\n"
	html += "</div>\n\n"
	return html

def _award_html(award):
	return '<span class="award" title="%s (%s)">%s</span>' %\
			(award.description, award.value, award.name)

def _player_html(player):
	return '<a class="team_%s" href="#%s">%s</a>' %\
			(player.team_color, player.slug_nick, player.nick)

def emph_percentage(hitrate, lower_bound, text=""):
	if hitrate == infinity:
		return "-"
	elif hitrate > lower_bound and hitrate != infinity:
		return "<strong>%.1f%%%s</strong>" % (hitrate, text)
	else:
		return "%.1f%%%s" % (hitrate, text)

def emph_int(value, lower_bound, text=""):
	if value > lower_bound:
		return "<strong>%d%s</strong>" % (value, text)
	else:
		return "%d%s" % (value, text)

_WEAPONS = [
# internal key, descriptive name, hitrate emphasize
	('gauntlet', 'Gauntlet', 1),
	('machinegun', "Machine&nbsp;gun", 30),
	('shotgun', 'Shotgun', 20),
	('rocketlauncher', 'Rocket&nbsp;launcher', 30),
	('plasmagun', 'Plasma&nbsp;gun', 20),
	('grenadelauncher', 'Grenade&nbsp;launcher', 10),
	('lightninggun', 'Lightning&nbsp;gun', 30),
	('railgun', 'Railgun', 40),
	('bfg', 'Big&nbsp;F***ing&nbsp;Gun', 1),
	('teleport', 'Teleport', 100.0),
]
_WEAPON_NAMES = dict()
for w, name, x in _WEAPONS:
	_WEAPON_NAMES[w] = name
_WEAPON_NAMES[None] = 'None'
_BORING_STATS = "elo team_damage_given team_kills flag_returns flag_assist_returns score suicides dmg_kill_ratio health armor base_defends carrier_defends flag_defends".split(" ")
def player_info(player):
	html = '<div class="player_stats" id="%s">\n' % player.slug_nick
	html += '<table class="player_info">\n'
	odd = Toggler("even", "odd")
	html += '<tr><td colspan="2" class="name team_%s"><strong>%s</strong> (<span class="elo" title="ELO Rating by frags">%d</span>)</td></tr>\n' % (player.team_color, player.nick, player.elo*1000)
	html += '<tr class="%s"><th>Weapons</th><td><span title="Most shots (normalized by reload times)">%s</span> / <span title="Most kills">%s</span></td></tr>\n' %\
			(odd, _WEAPON_NAMES[player.weapon_most_shots], _WEAPON_NAMES[player.weapon_most_kills])
	html += '<tr class="%s"><th>Player mostly</th><td>fragged by %s / fragging %s </td></tr>\n' % (odd, player.worst_enemy.nick, player.easiest_prey.nick)
	html += '<tr class="%s"><th>Frag rate</th><td>%s <span class="aside">(%s / %s)</span></td></tr>\n' % (odd, emph_percentage(player.fragrate*101.0, 100.0), emph_int(player.kill_count, 30), emph_int(player.death_count, 30))
	html += '<tr class="%s"><th>Damage rate</th><td>%s <span class="aside">(%d / %d)</span></td></tr>\n' % (odd, emph_percentage(player.damage_rate * 100.0, 110), player.damage_given, player.damage_received)
	html += '<tr class="%s"><th>Cap rate</th><td>%s <span class="aside">(%s / %s)</span></td></tr>\n' % (odd, emph_percentage(player.caprate * 100, 40), emph_int(player.flag_caps, 5), emph_int(player.flag_touches, player.flag_caps * 2))
	html += '<tr class="%s"><th>Streaks</th><td>%s &nbsp; %s &nbsp; %s</td></tr>\n' %\
		(odd, pluralize(player.kill_streak, "frag", 6), pluralize(player.death_streak, "death", 6), pluralize(player.cap_streak, "cap", 6))
	awards = ", ".join(_award_html(a) for a in player.awards)
	html += '<tr class="%s"><th>Awards&nbsp;(%d)</th><td>%s</td></tr>\n' % (odd, len(player.awards), awards)
	html += '<tr><td colspan="2">'
	html += '<div class="debug_stats">\n'
	for attr in _BORING_STATS:
		html += '<span>%s=%s</span>; \n' % (attr, getattr(player, attr))
	html += "</div>\n"
	html += '</tr></td>'
	html += "</table>\n"
	html += '<table class="weapon_info">\n'
	html += "<tr><th>Weapon</th><th>Hitrate</th><th>Fragrate</th></tr>\n"
	odd = Toggler("odd", "even")
	for w, wname, emph_rate in _WEAPONS:
		stats = getattr(player, w, None)
		if not stats:
			continue
		if int(stats['shots']) < 1:
			continue
		html += '<tr class="%s"><td>%s</td>' % (odd, wname)
		html += '<td class="rate">%s&nbsp;/&nbsp;%s = &nbsp; %s</td>' %\
						(stats['hits'], stats['shots'], emph_percentage(stats['hitrate']*100, emph_rate))
		html += '<td class="rate">%s&nbsp;/&nbsp;%s = &nbsp; %s</td>' %\
						(stats['kills'], stats['deaths'], emph_percentage(stats['killrate']*100, 200))
		html += "</tr>\n"
	html += "</table>\n"
	html += "</div>\n"
	return html

def kill_matrix(game):
	html = "<table>\n"
	def compare(p1, p2):
		return cmp(p1.team_id, p2.team_id) or cmp(p1.kill_count, p2.kill_count)
	def filter(p):
		return hasattr(p, 'player_kill_count')
	ps = game.sortedPlayers(compare=compare, include=filter)
	html += "<tr><th>Frag diff</th>"
	for p in ps:
		html += '<th class="team_%s">%s</th>' % (p.team_color, p.nick)
	html += "<th>Total</th></tr>\n"
	odd = Toggler("even", "odd")
	for p in ps:
		html += '<tr class="%s"><th class="team_%s">%s</th>' % (odd, p.team_color, p.nick)
		diff_count = 0
		for p2 in ps:
			kill_count = p.player_kill_count.get(p2, 0)
			death_count = p.player_death_count.get(p2, 0)
			diff = kill_count - death_count
			diff_count += diff
			teamkill = ""
			if p.team_id == p2.team_id and kill_count > 0:
				teamkill = ' teamkill'
			html += '<td class="kill_count %s" title="%d kills - %d deaths">%d</td>' % (teamkill, kill_count, death_count, diff)
		html += '<td class="kill_count">%s</td></tr>\n' % (diff_count)
	html += "</table>"
	return html
			
def award_table(players):
	html = ""
	awards = list()
	for p in players:
		if not hasattr(p, 'awards'):
			continue
		for a in p.awards:
			awards.append((p,a))
	awards.sort(cmp=lambda (p,a), (p2,a2): cmp(a.name,a2.name))
	# merge same awards
	awards_copy = awards[:]
	awards = []
	for p, a in awards_copy:
		if awards and a.name == awards[-1][1].name:
			awards[-1][0].append(p)
		else:
			awards.append(([p], a))
	# output
	for ps, a in awards:
		winners = " ".join(_player_html(p) for p in ps)
		award = _award_html(a)
		img = a.img_url or "media/award.png"
		img_base = os.path.basename(img)
		html += u'<div class="award"><div class="symbol"><img src="%s" alt="%s" /></div><div class="name">%s</div>\
		<div class="winner">%s</div></div>\n' % (img, img_base, award, winners)
	return html.encode('utf-8')

_HTML = """\
<html>
<head>
	<title>ArenaStats Game Report - %s</title>
	<link rel="stylesheet" type="text/css" href="media/style.css" /
</head>
<body>
	<h1>ArenaStats Game Report</h1>
	%s
	<div id="footer">
		This space intentionally left blank.
	</div>
</body></html>
"""

def html_report(game, levelshots):
	html = ""
	html += general_game_info(game, levelshots)
	html += '<div id="award_table">\n'
	html += award_table(game.sortedPlayers())
	html += '</div>\n'
	html += '<div id="kill_matrix">\n'
	html += kill_matrix(game)
	html += '</div>\n'
	html += '<div id="red_team" class="red_players">\n'
	for p in game.sortedPlayers():
		if hasattr(p, 'team_id') and p.team_id == 1:
			html += player_info(p)
	html += '</div>\n'
	html += '<div id="blue_team" class="blue_players">\n'
	for p in game.players.values():
		if hasattr(p, 'team_id') and p.team_id == 2:
			html += player_info(p)
	html += '</div>\n'
	return _HTML % (game.title, html)

