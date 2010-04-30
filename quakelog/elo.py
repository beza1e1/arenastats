"""
A rating system for player performance
"""

_RATINGS = dict()
_DEFAULT_RATING = 1.0
_MINIMUM_RATING = 0.001
_FRAGS_PER_SECOND = 0.016
_ABSORBER = 0.2

def get_rating(nick):
	if not nick in _RATINGS:
		_RATINGS[nick] = _DEFAULT_RATING
	return _RATINGS[nick]

def set_ratings(timelines):
	for timeline in timelines:
		for i in xrange(len(timeline)):
			p = timeline[i]
			if p.elo > 0:
				_RATINGS[p.nick] = p.elo

def elo_sum(game):
	elo_sum = 0
	for p in game.players.values():
		if not hasattr(p, 'team_id'):
			continue
		elo_sum += get_rating(p.nick)
	assert (elo_sum > 0), elo_sum
	return elo_sum

def predict_player(player, game, R):
	return get_rating(player.nick) / R
	
def rating_adaption(player, game, R):
	pred = predict_player(player, game, R)
	actual = float(player.kill_count) / game.frag_count
	d = actual - pred
	n = len(game.players) - 1 # subtract <world>
	adapt = d * _ABSORBER * n
	print "adapt %s %df %.3f %.3f %.3f" % (player.nick, player.kill_count, d, pred, actual)
	return adapt

def adapt_ratings(game):
	R = elo_sum(game)
	print "-"*20
	if game.frag_count == 0:
		return # nothing to adapt
	adaptions = dict()
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		p.elo = get_rating(p.nick) + rating_adaption(p, game, R)
		_RATINGS[p.nick] = p.elo

def rate(game):
	adapt_ratings(game)

