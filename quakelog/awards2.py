from copy import deepcopy
from utils import slugify, infinity

class Award:
	def __init__(self, name, img_url, description):
		self.name = name
		if not img_url:
			self.img_url = "media/awards/" + slugify(name).lower() + ".png"
		else:
			self.img_url = "media/awards/" + img_url
		self.description = description
		self.value = None

class Condition:
	def __add__(self, y):
		return combine(self, y)
	def findValue(self, players, maxima):
		raise NotImplemented()
	def bestPlayers(self, players):
		raise NotImplemented()
	
class MinMax(Condition):
	def __init__(self, attrib, boundary):
		self.attrib = attrib
		self.boundary = boundary
		self._sattrib = self.prefix+attrib
	def findValue(self, players, maxima):
		if self._sattrib in maxima:
			return # already done by someone else
		maximum = self.boundary
		for p in players:
			if "-" in self.attrib:
				weapon, attr = self.attrib.split("-")
				pattrib = getattr(p, weapon, dict()).get(attr, self.boundary)
			else:
				pattrib = getattr(p, self.attrib, self.boundary)
			maximum = self.better(pattrib, maximum)
		maxima[self._sattrib] = maximum
	def bestPlayers(self, players, maxima):
		best = set()
		for p in players:
			if "-" in self.attrib:
				weapon, attr = self.attrib.split("-")
				if not hasattr(p, weapon):
					continue
				if not attr in getattr(p, weapon):
					continue
				value = getattr(p, weapon)[attr]
			else:
				if not hasattr(p, self.attrib):
					continue
				value = getattr(p, self.attrib)
			if value == maxima[self._sattrib]:
				best.add(p)
		return best
	
class max(MinMax):
	prefix = "max_"
	def __init__(self, attrib, boundary=0):
		MinMax.__init__(self, attrib, boundary)
	def better(self, x, y):
		if x > y:
			return x
		else:
			return y

class min(MinMax):
	prefix = "min_"
	def __init__(self, attrib, boundary=infinity):
		MinMax.__init__(self, attrib, boundary)
	def better(self, x, y):
		if x < y:
			return x
		else:
			return y

class combine(Condition):
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def findValue(self, players, maxima):
		self.x.findValue(players, maxima)
		self.y.findValue(players, maxima)
	def bestPlayers(self, players, maxima):
		x = self.x.bestPlayers(players, maxima)
		y = self.y.bestPlayers(players, maxima)
		return x.intersection(y)

_AWARDS = [
	(max('armor') + max('health'),\
	 		Award("Collector", None, "Most armor and health")),
	(max('damage_given') + min('damage_received'),\
	 		Award("Ninja", None, "Most damage given and least received")),
	(max('railgun-hitrate') + max('railgun-kills'),\
	 		Award("Sniper", None, "Best hitrate and most frags with Railgun")),
]

def give_awards(players):
	maxima = dict()
	for condition, award in _AWARDS:
		condition.findValue(players, maxima)
	for condition, award in _AWARDS:
		best = condition.bestPlayers(players, maxima)
		for p in best:
			p.awards.append(award)
		
