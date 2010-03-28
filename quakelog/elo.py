"""
A rating system for player performance
"""

_RATINGS = dict()
_DEFAULT_RATING = 1.0

def get_rating(nick):
	if not nick in _RATINGS:
		_RATINGS[nick] = _DEFAULT_RATING
	return _RATINGS[nick]

def predict_game(game):
	assert game.gametype == "Capture the Flag", game.gametype
	rsum = [0.0] * 4
	rcount = [0] * 4
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		rsum[p.team_id] += get_rating(p.nick)
		rcount[p.team_id] += 1
	for i in range(len(rsum)):
		rsum[i] = rsum[i] * rcount[i]
	sum = rsum[1] + rsum[2]
	return rsum[1] / sum, rsum[2] / sum
	
def rating_adaption(game):
	red_p, blue_p = predict_game(game)
	red  = game.teams[1].capture_count
	blue = game.teams[2].capture_count
	red_pc = game.teams[1].player_count
	blue_pc = game.teams[2].player_count
	def formula(x, y):
		return float(x - y) / (y + 1)
	red_f, blue_f = formula(red, blue), formula(blue, red)
	def formula(f, pred, count):
		return f * (((1 - pred)**2) / count)
	return formula(red_f, red_p, red_pc), formula(blue_f, blue_p, blue_pc)

def adapt_ratings(game):
	red_a, blue_a = rating_adaption(game)
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		if p.team_id == 1:
			_RATINGS[p.nick] += red_a
		elif p.team_id == 2:
			_RATINGS[p.nick] += blue_a
	
def rate(game):
	adapt_ratings(game)
