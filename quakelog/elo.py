"""
A rating system for player performance
"""

_RATINGS = dict()
_DEFAULT_RATING = 1.0
_MINIMUM_RATING = 0.001
_FRAGS_PER_SECOND = 0.016
_ABSORBER = 0.3

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

def team_average(game, team_id):
	avg = (0.0, 0)
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		elif p.team_id == team_id:
			avg = (avg[0] + get_rating(p.nick), avg[1]+1)
	return avg[0] / avg[1]

def other_team(team_id):
	if team_id == 1:
		return 2
	elif team_id == 2:
		return 1
	else:
		return team_id

def predict_player(player, game):
	avg = team_average(game, other_team(player.team_id))
	rel_frags = (avg + get_rating(player.nick)) / avg
	# TODO time could be wrong if the player joined later
	return game.game_duration * _FRAGS_PER_SECOND * rel_frags
	
def rating_adaption(player, game):
	pred = predict_player(player, game)
	adapt = _ABSORBER * ((player.kill_count - pred) / game.frag_count)
	if get_rating(player.nick) - adapt < _MINIMUM_RATING:
		adapt = _MINIMUM_RATING - get_rating(player.nick)
	return adapt

def adapt_ratings(game):
	adaptions = dict()
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		p.elo = get_rating(p.nick) + rating_adaption(p, game)
		_RATINGS[p.nick] = p.elo

def rate(game):
	adapt_ratings(game)

