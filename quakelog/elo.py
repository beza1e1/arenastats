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
	red = 0.0
	blue = 0.0
	for pid, p in game.players.items():
		if not hasattr(p, 'team_id'):
			continue
		if p.team_id == 1:
			red += get_rating(p.nick)
		elif p.team_id == 2:
			blue += get_rating(p.nick)
	sum = red + blue
	return red / sum, blue / sum
	
def rating_adaption(game):
	pred, pblue = predict_game(game)
	red  = game.teams[1].capture_count
	blue = game.teams[2].capture_count
	red, blue = {True: (1,0), False: (0,1)}[red > blue]
	red_pc  = game.teams[1].player_count
	blue_pc = game.teams[2].player_count
	return float(red - pred) / red_pc,\
		   float(blue - pblue) / blue_pc

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
