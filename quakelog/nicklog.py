from datetime import datetime
from utils import slugify
from replay import Player, _ZERO_PROPERTIES, _STAT_WEAPONS

_LOG_PROPERTIES = _ZERO_PROPERTIES[:]

def _str_player_line(player):
	strings = list()
	strings.append('"%s"' % player.nick)
	for prop in _LOG_PROPERTIES:
		strings.append("%s:%d" % (prop, getattr(player, prop)))
	for weapon in _STAT_WEAPONS.values():
		w = getattr(player, weapon)
		strings.append("%s:%s:%s:%s:%s" % (weapon, w.get('shots',0), w.get('hits',0), w['kills'], w['deaths']))
	return " ".join(strings)

_COUNT = 1
def player_line(player):
	global _COUNT
	out = datetime.now().strftime("%Y.%m.%d-%H:%M:%S-")
	out += "%05d " % _COUNT
	_COUNT += 1
	out += _str_player_line(player)
	return out

def read_player_line(line):
	n1 = line.index('"')
	n2 = line.index('"', n1+1)
	nick = line[n1+1:n2]
	p = Player()
	setattr(p, 'nick', nick)
	setattr(p, 'slug_nick', slugify(p.nick))
	attribs = line[n2+2:].split(" ")
	for attr in attribs[2:]:
		attr = attr.split(":")
		if len(attr) == 2:
			key, val = attr
			setattr(p, key, int(val))
		elif len(attr) == 5:
			weapon, shots, hits, kills, deaths = attr
			try:
				hitrate = float(hits) / float(shots)
			except ZeroDivisionError:
				hitrate = 0.0
			setattr(p, weapon, dict(shots=int(shots), hits=int(hits), kills=int(kills), deaths=int(deaths), hitrate=hitrate))
		else:
			print attr
	for prop in _LOG_PROPERTIES:
		if not hasattr(p, prop):
			setattr(p, prop, 0)
	return p


def merge_player_lines(lines):
	players = dict()
	for line in lines:
		player = read_player_line(line)
		if not player.nick in players:
			players[player.nick] = [player]
		else:
			players[player.nick].append(player)
	for nick, player_timeline in players.items():
		yield player_timeline

def append_nicklog(fh, game):
	for player in game.players.values():
		if not hasattr(player, 'team_id'):
			continue
		fh.write("%s\n" % player_line(player))

def load_timelines(options):
	fh = open(options.nicklog)
	timelines = list(merge_player_lines(fh))
	fh.close()
	return timelines

