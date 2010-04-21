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
		(Award("Collector", None, "Most armor and health collected"),
				max('armor') + max('health')),
		(Award("Power Up", None, "Most Regen, Mega Health, Quad, Haste, MedKit, Teleporter, Flight and Battle Suit collected"),
		 		max('invis_count')+max('regen_count')+max('mega_health_count')+max('quad_count')+max('haste_count')+max('medkit_count')+max('teleporter_count')+max('flight_count')+max('battle_suit_count')),
		(Award("The Tank", None, "Most armor and least deaths"),
				max('armor') + min('death_count')),
		(Award("Ninja", None, "Most damage given and least received"),
				max('damage_given') + min('damage_received')),
		(Award("Punching Bag", None, "Most damage received and least given"),
				max('damage_received') + min('damage_given')),
		(Award("Flag Runner", None, "Most flag caps and returns"),
				max('flag_caps',1) + max('flag_returns',1)),
		(Award("Who needs enemies?", None, "Most suicides and team damage"),
				max('suicides',1) + max('team_damage_given') + max('team_kills',1)),
		(Award("Mole", None, "Most team damage and team frags"),
				max('team_kills',1) + max('team_damage_given',1)),
		(Award("Defender", None, "Most base, flag and carrier defends"),
				max('base_defends',1) + max('flag_defends',1) + max('carrier_defends',1)),
		(Award("Lucky Bastard", None, "Least damage per kill ratio and deaths"),
				min('dmg_kill_ratio') + min('death_count')),
		(Award("Berserker", None, "Highest kill streak and most frags"),
				max('kill_count') + max('kill_streak')),
		(Award("Streaker", None, "Highest kill, death and cap streak"),
				max('kill_streak') + max('death_streak') + max('cap_streak')),
		(Award("Clucking Hen", None, "Most flag carrier frags and flag returns"),
				max('flag_carrier_kills',1) + max('flag_returns',1)),
		(Award("Sniper", None, "Best hitrate and most frags with Railgun"),
				max('railgun-hitrate') + max('railgun-kills',1)),
		(Award("Bomber", None, "Most shots with rocket and grenade launcher"),
				max('rocketlauncher-shots',1) + max('grenadelauncher-shots',1)),
		(Award("Pummel King", None, "Most shots and frags with Gauntlet"),
				max('gauntlet-shots') + max('gauntlet-kills',1)),
		(Award("Telefragger", None, "Most telefrags"),
				max('teleport-kills',1)),
		(Award("Hot Shot", None, "Most shots with machine, lightning and plasma gun"),
				max('machinegun-shots',1) + max('lightninggun-shots',1) + max('plasmagun-shots',1)),
		(Award("Sudden Death Decider", None, "Final cap in sudden death overtime"),
				max('sudden_death_decider',1)),
		(Award("Chatterbox", None, "Most chatted characters"),
				max('chat_length',40)),
]

def give_awards(players):
	maxima = dict()
	for award, condition in _AWARDS:
		condition.findValue(players, maxima)
	for award, condition in _AWARDS:
		best = condition.bestPlayers(players, maxima)
		for p in best:
			p.awards.append(award)
		
