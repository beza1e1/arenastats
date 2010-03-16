from copy import deepcopy

class Award:
	def __init__(self, name, img_url, description):
		self.name = name
		self.img_url = img_url
		self.description = description
		self.value = None

## minimum, attribute name, award
_MAX_AWARDS = [
	(40, 'kill_count', Award("Death Eater", None, "most kills")),
	(1400, 'health', Award("Workout Warrior", None, "most health collected")),
	(1400, 'armor', Award("The Tank", None, "Most armor collected")),
	(6000, 'damage_received', Award("Punching Bag", None, "most damage received")),
	(6000, 'damage_given', Award("Berserker", None, "most damage given")),
	(2, 'invis_count', Award("Hollow Man", None, "most often picked up Invisibility")),
	(2, 'regen_count', Award("Snake Blood", None, "most often picked up Regen")),
	(3, 'mega_health_count', Award("Mega Man", None, "most often picked up Mega Health")),
	(2, 'quad_count', Award("Demolition Man", None, "most often picked up Quad")),
	(2, 'haste_count', Award("Speeder", None, "Most often picked up Haste")),
	(2, 'medkit_count', Award("The Doc", None, "most often picked up the Medikit")),
	(5, 'flag_caps', Award("Flag Runner", None, "most flag captures")),
	(7, 'flag_returns', Award("Clucking Hen", None, "most flag returns")),
#(5, 'flag_assist_returns', Award("JIT Clucking Hen", None, "most flag assist returns")),
	(5, 'flag_carrier_kills', Award("Headhunter", None, "most flag carrier kills")),
	(3, 'suicides', Award("Suicide Bunny", None, "most suicides")),
	(3, 'team_kills', Award("Frag is Frag", None, "most team kills")),
	(250, 'team_damage_given', Award("Colorblind", None, "Most team damage given")),
	(3, 'base_defends', Award("Housekeeper", None, "most base defends")),
	(3, 'flag_defends', Award("Flag Paladin", None, "most flag defends")),
	(3, 'carrier_defends', Award("Carrier Paladin", None, "most carrier defends")),
	(50, 'chat_length', Award("Chatterbox", None, "most chatted characters")),
	(6, 'kill_streak', Award("Killing Spree", None, "highest kill streak")),
	(7, 'death_streak', Award("Frustrated Dead", None, "highest death streak")),
	(2, 'cap_streak', Award("Capture King", None, "highest cap streak")),
	(1.5, 'dmg_kill_ratio', Award("Hard Worker", None, "Most damage per kill")),
]
## maximum, attribute name, award
_ULTIMATE_MAX = 1000000
_MIN_AWARDS = [
	(1.9, 'dmg_kill_ratio', Award("Lucky Bastard", None, "least damage per kill")),
	(1000, 'team_damage_given', Award("Friendliest Fire", None, "least team damage")),
	(15, 'death_count', Award("Survivor", None, "Least deaths")),
]
## minimum, weapon, weapon attribute, award
_MAX_WEAPONS = [
	(3, 'gauntlet', 'kills', Award("Pummel King", None, "most kills with gauntlet")),
	(4, 'gauntlet', 'shots', Award("Close Combateer", None, "most shots with gauntlet")),
	(10, 'shotgun', 'kills', Award("Hot Shot", None, "most kills with shotgun")),
	(400, 'shotgun', 'shots', Award("Pumping Player", None, "most shots with shotgun")),
	(400, 'machinegun', 'shots', Award("Trigger Happy", None, "most shots with machine gun")),
	(5, 'machinegun', 'kills', Award("Brave Soldier", None, "most kills with machine gun")),
	(100, 'rocketlauncher', 'shots', Award("Rocketeer", None, "most shots with rocket launcher")),
	(50, 'rocketlauncher', 'hits', Award("Cruise Missile", None, "most hits with rocket launcher")),
	(4, 'grenadelauncher', 'kills', Award("Bomber", None, "most kills with grenade launcher")),
	(0.2, 'grenadelauncher', 'hitrate', Award("Trajectorist", None, "best hitrate with grenade launcher")),
	(1500, 'lightninggun', 'shots', Award("High Voltage", None, "most shots with lightning gun")),
	(20, 'lightninggun', 'kills', Award("Electrocutioner", None, "most kills with lightning gun")),
	(20, 'plasmagun', 'hitrate', Award("Plasma hitter", None, "best hitrate with plasma gun")),
	(140, 'plasmagun', 'shots', Award("Plasmatic", None, "Most shots with plasma gun")),
	(10, 'railgun', 'kills', Award("Sniper", None, "most kills with railgun")),
	(50, 'railgun', 'shots', Award("Railfreak", None, "most shots with railgun")),
	(0.4, 'railgun', 'hitrate', Award("Railmaster", None, "best hitrate with railgun")),
	(0, 'teleport', 'kills', Award("Telefragger", None, "most kills by teleport")),
]
_META_AWARDS = [
	(('Sniper', 'Railfreak', 'Railmaster'), Award("Mr RAIL", None, "Highest hitrate and most kills and shots with railgun")),
	(('Housekeeper', 'Flag Paladin', 'Carrier Paladin'), Award("The WALL", None, "Most base, flag and carrier defends")),
	(('Pummel King', 'Close Combateer'), Award("Mr GAUNTLET", None, "Most shots and kills with the gauntlet")),
	(('Berserker', 'Killing Spree'), Award("Wild Berserker", None, "Highest kill streak and most damage given")),
]
def remove_if_needed_all_present(needed_awards, player):
	filtered_awards = list()
	remove_awards = list()
	for award in player.awards:
		filtered_awards.append(award)
		for na in needed_awards:
			if na == award.name:
				remove_awards.append(award)
				filtered_awards.remove(award)
				break
	if len(needed_awards) == len(remove_awards):
		player.awards = filtered_awards
		return True
	else:
		return False

def give_awards(players):
	maxima = dict()
	minima = dict()
	for min, attr, award in _MAX_AWARDS:
		maxima[attr] = (0, [])
	for max, attr, award in _MIN_AWARDS:
		minima[attr] = (_ULTIMATE_MAX, [])
	for min, attr, subattr, award in _MAX_WEAPONS:
		if not attr in maxima:
			maxima[attr] = dict()
		maxima[attr][subattr] = (0, [])
	for p in players:
		if not hasattr(p, 'awards'):
			continue
		for min, attr, award in _MAX_AWARDS: # maximal awards
			val = getattr(p, attr, 0)
			if val > min and val > maxima[attr][0]:
				maxima[attr] = (val, [p])
			elif val > 0 and val == maxima[attr][0]:
				val, ps = maxima[attr]
				ps.append(p)
		for max, attr, award in _MIN_AWARDS: # minimal awards
			val = getattr(p, attr, None)
			if val == None:
				continue
			if val < max and val < minima[attr][0]:
				minima[attr] = (val, [p])
			elif val == minima[attr][0]:
				val, ps = minima[attr]
				ps.append(p)
		for min, attr, subattr, award in _MAX_WEAPONS: # maximal weapon awards
		 	att = getattr(p, attr, dict())
			val = att.get(subattr, 0)
			assert not isinstance(val, str), (attr, subattr, att, val)
			if val > min and val > maxima[attr][subattr][0]:
				maxima[attr][subattr] = (val, [p])
			elif val > min and val == maxima[attr][subattr][0]:
				val, ps = maxima[attr][subattr]
				ps.append(p)
	for min, attr, award in _MAX_AWARDS: # maximal awards
		award.value, ps = maxima[attr]
		for p in ps:
			p.awards.append(deepcopy(award))
		else:
			"Nobody is", award.name
	for max, attr, award in _MIN_AWARDS: # minimal awards
		award.value, ps = minima[attr]
		for p in ps:
			p.awards.append(deepcopy(award))
		else:
			"Nobody is", award.name
	for min, attr, subattr, award in _MAX_WEAPONS: # maximal weapon awards
		award.value, ps = maxima[attr][subattr]
		for p in ps:
			p.awards.append(deepcopy(award))
		else:
			"Nobody is", award.name
	for p in players:
		if not hasattr(p, 'awards'):
			continue
		for needed, award in _META_AWARDS:
			if remove_if_needed_all_present(needed, p):
				p.awards.append(award)
	# Booby prize for those, who got nothing ...
	for p in players:
		if hasattr(p, 'awards') and not p.awards:
			p.awards.append(Award("Booby Prize", None, "Good luck next time. You need it."))


