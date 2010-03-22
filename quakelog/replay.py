from tokenizer import GameEvent, NewClient, PlayerinfoChange, KillClient, ItemPickup, Kill, InitGame, TeamName, Chat, WeaponStats, EndGame, ServerTime, TeamScore, FlagCapture, FlagReturn, FlagAssistReturn, FlagCarrierKill, FlagDefend, BaseDefend, FlagAssistFrag, CarrierDefend, Score
from awards import give_awards
from utils import slugify

infinity = float("infinity")

class Item:
	def use(self, player):
		print player.nick, "uses generic item", self.name

class Ammo(Item):
	def use(self, player):
		pass

class Weapon(Item):
	def use(self, player):
		pass

class Armor(Item):
	def __init__(self, armor):
		self.armor = armor
	def use(self, player):
		player.armor += self.armor

class Health(Item):
	def __init__(self, health):
		self.health = health
	def use(self, player):
		player.health += self.health

class MegaHealth(Health):
	def use(self, player):
		Health.use(self, player)
		player.mega_health_count += 1

class Regen(Item):
	def use(self, player):
		player.regen_count += 1

class Quad(Item):
	def use(self, player):
		player.quad_count += 1

class Haste(Item):
	def use(self, player):
		player.haste_count += 1

class Invisibility(Item):
	def use(self, player):
		player.invis_count += 1

class Medkit(Item):
	def use(self, player):
		player.medkit_count += 1

class Flight(Item):
	def use(self, player):
		player.flight_count += 1

class Teleporter(Item):
	def use(self, player):
		player.hand_teleporter_count += 1

class BattleSuit(Item):
	def use(self, player):
		player.battle_suit_count += 1

class Flag(Item):
	def __init__(self, team_id):
		self.team_id = team_id
	def use(self, player):
		if player.team_id == self.team_id:
			pass # flag return, accounted by FlagReturn event
		else:
			player.flag_touches += 1

_WEAPONS = {
	"weapon_gauntlet": Weapon(),
	"weapon_shotgun": Weapon(),
	"weapon_lightning": Weapon(),
	"weapon_plasmagun": Weapon(),
	"weapon_rocketlauncher": Weapon(),
	"weapon_grenadelauncher": Weapon(),
	"weapon_railgun": Weapon(),
	"weapon_bfg": Weapon(),
	"ammo_bullets": Ammo(),
	"ammo_cells": Ammo(),
	"ammo_slugs": Ammo(),
	"ammo_rockets": Ammo(),
	"ammo_grenades": Ammo(),
	"ammo_lightning": Ammo(),
	"ammo_shells": Ammo(),
	"ammo_bfg": Ammo(),
	"item_health_small": Health(10),
	"item_health": Health(25),
	"item_health_large": Health(50),
	"item_health_mega": MegaHealth(100),
	"item_armor_shard": Armor(25),
	"item_armor_combat": Armor(50),
	"item_armor_body": Armor(100),
	"team_CTF_redflag": Flag(1),
	"team_CTF_blueflag": Flag(2),
	"item_regen": Regen(),
	"holdable_medkit": Medkit(),
	"item_quad": Quad(),
	"item_haste": Haste(),
	"item_invis": Invisibility(),
	"item_flight": Flight(),
	"item_enviro": BattleSuit(),
	"holdable_teleporter": Teleporter(),
}

_WORLD_ID = 1022 # Really?
_STAT_WEAPONS = {
	'Gauntlet': "gauntlet", 
	'R.Launcher': "rocketlauncher", 
	'Shotgun': "shotgun", 
	'Plasmagun': "plasmagun", 
	'Railgun': "railgun", 
	'G.Launcher': "grenadelauncher", 
	'LightningGun': "lightninggun", 
	'MachineGun': "machinegun",
	'World aka Suicides': 'environment',
	'BFG': 'bfg',
	'Telefrag': 'teleport',
}
def statdict(weapon_stats):
	ws = weapon_stats
	sd = dict(shots=ws[0], hits=ws[1], A=ws[2], B=ws[3])
	try:
		sd['hitrate'] = float(sd['hits']) / float(sd['shots'])
	except ZeroDivisionError:
		sd['hitrate'] = 0.0
	return sd

_TEAM_COLORS = {
	0: "white",
	1: "red",
	2: "blue",
	3: "green",
}

_WEAPON_RELOAD_TIMES = { # in seconds
	"gauntlet": 0.4, 
	"rocketlauncher": 0.8, 
	"shotgun": 1.0, 
	"plasmagun": 0.1, 
	"railgun": 1.5, 
	"grenadelauncher": 0.8, 
	"lightninggun": 0.05, 
	"machinegun": 0.1,
	'environment': 0.01,
	'teleport': 0.01,
	'bfg': 0.2,
}

_ZERO_PROPERTIES = [
	'quad_count', 'regen_count', 'haste_count', 'mega_health_count',
	'invis_count', 'medkit_count', 'flag_returns', 'flag_touches',
	'flag_caps', 'flag_assist_returns', 'flag_assist_kills', 'suicides',
	'kill_count', 'death_count', 'team_kills', 'flag_defends',
	'base_defends', 'carrier_defends', 'flag_carrier_kills',
	'chat_length', 'kill_streak', 'current_kill_streak', 'death_streak',
	'current_death_streak', 'cap_streak', 'current_cap_streak', 'score',
	'health', 'armor', 'sudden_death_decider', 'flight_count',
	'damage_given', 'damage_received', 'team_damage_given',
	'hand_teleporter_count', 'battle_suit_count'
]
class Player:
	def initFromToken(self, tok):
		assert isinstance(tok, NewClient), tok
		self.id = tok.client_id
		self.team_id = -1
		self.disconnected = False
		self.nick = "no_nick_yet"
		self.chats = list()
		self.player_kill_count = dict()
		self.player_death_count = dict()
		for weapon in _STAT_WEAPONS.values():
			setattr(self, weapon, dict(kills=0, deaths=0, shots=0, hits=0))
		self.awards = list()
		for prop in _ZERO_PROPERTIES:
			setattr(self, prop, 0)
		self.respawn()
	def update(self, tok):
		assert isinstance(tok, PlayerinfoChange), tok
		self.nick = tok.nick
		self.team_id = int(tok.team_id)
		self.team_color = _TEAM_COLORS[self.team_id]
	def pickupItem(self, item_name):
		item = _WEAPONS.get(item_name, None)
		if not item:
			print self.nick, "picks up unknown item", item_name
		else:
			item.use(self)
	def kill(self, victim, weapon):
		self.kill_count += 1
		victim.death_count += 1
		if not victim in self.player_kill_count:
			self.player_kill_count[victim] = 0
		self.player_kill_count[victim] += 1
		if not self in victim.player_death_count:
			victim.player_death_count[self] = 0
		victim.player_death_count[self] += 1
		getattr(self, weapon)['kills'] += 1
		getattr(victim, weapon)['deaths'] += 1
		self.current_kill_streak += 1
		self.current_death_streak = 0
		if self.team_id == victim.team_id:
			self.team_kills += 1
		victim.respawn()
	def chat(self, message):
		self.chats.append(message)
	def respawn(self):
		if self.current_kill_streak == 0:
			self.current_death_streak += 1
		self.death_streak = max(self.death_streak, self.current_death_streak)
		self.kill_streak = max(self.kill_streak, self.current_kill_streak)
		self.cap_streak = max(self.cap_streak, self.current_cap_streak)
		self.current_kill_streak = 0
		self.current_cap_streak = 0
		self.flag = None
	def captureFlag(self):
		self.flag_caps += 1
		self.current_cap_streak += 1
	def finalize(self):
		self.gauntlet['shots'] = max(self.gauntlet['shots'], self.gauntlet['hits']) # Gauntlet does not record shots it seems
		self.teleport['shots'] = self.teleport['kills']
		max_shots = (0, None)
		max_kills = (0, None)
		for weapon in _STAT_WEAPONS.values():
			sattr = getattr(self, weapon)
			kills = float(sattr['kills'])
			if kills > max_kills[0]:
				max_kills = (kills, weapon)
			relative_shots = sattr['shots'] * _WEAPON_RELOAD_TIMES[weapon]
			if relative_shots > max_shots[0]:
				max_shots = (relative_shots, weapon)
			deaths = float(sattr['deaths'])
			if deaths == 0:
				sattr['killrate'] = infinity
			else:
				sattr['killrate'] = kills / deaths
		self.weapon_most_shots = max_shots[1]
		self.weapon_most_kills = max_kills[1]
		max_kills = (0, None)
		for player, kills in self.player_kill_count.items():
			if kills > max_kills[0]:
				max_kills = (kills, player)
		self.easiest_prey = max_kills[1]
		max_deaths = (0, None)
		for player, deaths in self.player_death_count.items():
			if deaths > max_deaths[0]:
				max_deaths = (deaths, player)
		self.worst_enemy = max_deaths[1]
	def setStats(self, stats):
		self.damage_given = int(stats['Given'][0])
		self.damage_received = int(stats['Recvd'][0])
		try:
			self.team_damage_given = stats['TeamDmg'][0]
		except KeyError:
		 	self.team_damage_given = 0
		self.health = int(stats['Health'][0])
		for weapon, wattr in _STAT_WEAPONS.items():
			weapon_stats = statdict(stats.get(weapon, [0,0,0,0]))
			sattr = getattr(self, wattr)
			for key, val in weapon_stats.items():
				if not key in sattr or sattr[key] == 0:
					sattr[key] = val
				else:
					print "ignore weapon stats", key, val
	def serialize(self):
		strings = list()
		strings.append('"%s"' % self.nick)
		for prop in _ZERO_PROPERTIES:
			strings.append("%s:%d" % (prop, getattr(self, prop)))
		for weapon in _STAT_WEAPONS.values():
			w = getattr(self, weapon)
			strings.append("%s:%s:%s:%s:%s" % (weapon, w.get('shots',0), w.get('hits',0), w['kills'], w['deaths']))
		return " ".join(strings)
	def _get_caprate(self):
		if self.flag_touches == 0:
			return infinity
		else:
			return float(self.flag_caps) / float(self.flag_touches)
	caprate = property(_get_caprate)
	def _get_dmgrate(self):
		if self.damage_received == 0:
			return infinity
		else:
			return float(self.damage_given) / float(self.damage_received)
	damage_rate = property(_get_dmgrate)
	def _get_dmg_kill_ratio(self):
		if self.kill_count == 0:
			return infinity
		else:
			return (float(self.damage_given) / 100) / float(self.kill_count)
	dmg_kill_ratio = property(_get_dmg_kill_ratio)
	def _get_slug_nick(self):
		return slugify(self.nick)
	slug_nick = property(_get_slug_nick)

class World(Player):
	def __init__(self):
		self.id = _WORLD_ID
		self.nick = "<world>"
	def kill(self, victim, weapon):
		victim.suicides += 1
		victim.respawn()

class Team:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.capture_count = 0
		self.player_count = 0

_COUNT = 1
def gen_game_name(token):
	assert isinstance(token, InitGame)
	global _COUNT
	_COUNT += 1
	mapname = getattr(token, 'mapname', 'no_map')
	return "%05d_%s" % (_COUNT, mapname)

_GAME_TYPES = ['nothing','Free for All', 'Team Deathmatch', 'Tournament', 'Capture the Flag']

_WEAPON_DESC = {
	'MOD_GAUNTLET': 'gauntlet',
	'MOD_MACHINEGUN': 'machinegun',
	'MOD_SHOTGUN': 'shotgun',
	'MOD_LIGHTNING': 'lightninggun',
	'MOD_PLASMA': 'plasmagun',
	'MOD_PLASMA_SPLASH': 'plasmagun',
	'MOD_RAILGUN': 'railgun',
	'MOD_ROCKET': 'rocketlauncher',
	'MOD_ROCKET_SPLASH': 'rocketlauncher',
	'MOD_GRENADE': 'grenadelauncher',
	'MOD_GRENADE_SPLASH': 'grenadelauncher',
	'MOD_SUICIDE': 'environment',
	'MOD_BFG': 'bfg',
	'MOD_BFG_SPLASH': 'bfg',
	'MOD_TELEFRAG': 'teleport', 
	'MOD_SWITCHTEAM': 'environment',
}
class Game:
	def __init__(self, token):
		assert isinstance(token, InitGame)
		try:
			self.gametype = _GAME_TYPES[int(token.g_gametype)]
		except IndexError:
		 	self.gametype = "unknown game type"
		self.mapname = getattr(token, 'mapname', 'no_map')
		self.name = gen_game_name(token)
		self.finished = False
		self.frag_count = 0
		self.players = dict()
		self.players[_WORLD_ID] = World()
		self.players_eternal = list() # still alive after disconnect
		self.teams = dict()
		self.teams[3] = Team(3, "Observers")
		self.start_time = token.time
		self.game_duration = float(token.timelimit) * 60.0
		self.end_time = self.start_time + self.game_duration
	def nextStep(self, token):
		if isinstance(token, NewClient):
			if self.finished:
				return
			p = Player()
			p.initFromToken(token)
			self.players[token.client_id] = p
			self.players_eternal.append(p)
		elif isinstance(token, PlayerinfoChange):
			if self.finished:
				return
			self.players[token.client_id].update(token)
			for t in self.teams.values():
				t.player_count = 0
			for p in self.players.values():
				if hasattr(p, 'team_id') and p.team_id in self.teams.keys():
					self.teams[p.team_id].player_count += 1
		elif isinstance(token, EndGame):
			self.finished = True
		elif isinstance(token, KillClient):
			p = self.players.get(token.client_id, None)
			if p: # ignore non existant disconnects
				p.disconnect = True
		elif isinstance(token, TeamScore):
			t = self.teams[token.team_id]
			t.capture_count = token.capture_count
		elif isinstance(token, TeamName):
			t = Team(token.team_id, token.name)
			self.teams[token.team_id] = t
		elif isinstance(token, ItemPickup):
			p = self.players[token.client_id]
			p.pickupItem(token.item)
		elif isinstance(token, WeaponStats):
			p = self.players.get(token.client_id, None)
			if p: # ignore weapon stats of non existant players
				p.setStats(token.stats)
		elif isinstance(token, ServerTime):
			self.datetime = token.datetime
			self.title = "%s_%s" % (self.datetime.strftime("%Y-%m-%d"), self.mapname)
		elif isinstance(token, Chat):
			for p in self.players.values():
				if p.nick == token.nick:
					p.chat(token.message)
					p.chat_length += len(token.message)
		elif isinstance(token, Kill):
			p = self.players[token.client_id]
			victim = self.players[token.victim_id]
			weapon = _WEAPON_DESC.get(token.weapon_description, token.weapon_description)
			p.kill(victim, weapon)
			self.frag_count += 1
		elif isinstance(token, FlagCapture):
			p = self.players[token.client_id]
			p.captureFlag()
			if token.time > self.end_time:
				p.sudden_death_decider += 1
		elif isinstance(token, FlagReturn):
			p = self.players[token.client_id]
			p.flag_returns += 1
		elif isinstance(token, FlagAssistReturn):
			p = self.players[token.client_id]
			p.flag_assist_returns += 1
		elif isinstance(token, FlagAssistFrag):
			p = self.players[token.client_id]
			p.flag_assist_kills += 1
		elif isinstance(token, FlagCarrierKill):
			p = self.players[token.client_id]
			p.flag_carrier_kills += 1
		elif isinstance(token, FlagDefend):
			p = self.players[token.client_id]
			p.flag_defends += 1
		elif isinstance(token, BaseDefend):
			p = self.players[token.client_id]
			p.base_defends += 1
		elif isinstance(token, CarrierDefend):
			p = self.players[token.client_id]
			p.carrier_defends += 1
		elif isinstance(token, Score):
			p = self.players[token.client_id]
			p.score = token.score
		else:
			print "Unknown token", token
	def sortedPlayers(self, compare=None, include=None):
		if not compare:
			compare = lambda x,y: cmp(x.nick.lower(), y.nick.lower())
		return sorted(filter(include, self.players.values()), compare)
	def finalize(self):
		for p in self.players.values():
			if hasattr(p, 'team_id'):
				p.finalize()

def replay_games(game_events):
	g = None
	for event in game_events:
		if event.game_start:
			if g:
				print "Log file broken (illegal game start) in line", event.line_count
			g = Game(event)
		elif event.game_destroy:
			if not g:
				print "Log file broken (illegal game shutdown) in line", event.line_count
			elif g.finished:
				g.finalize()
				give_awards(g.players.values())
				yield g
			g = None
		else:
			if g:
				g.nextStep(event)
