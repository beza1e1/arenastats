from copy import deepcopy

class Award:
	def __init__(self, name, img_url, description):
		self.name = name
		self.img_url = img_url
		self.description = description
		self.value = None

## minimum, attribute name, award
_MAX_AWARDS = [
	(40, 'kill_count', Award("Death Eater", None, "Most kills")),
	(1400, 'health', Award("Workout Warrior", None, "Most health collected")),
	(1600, 'armor', Award("The Tank", None, "Most armor collected")),
	(6000, 'damage_received', Award("Punching Bag", None, "Most damage received")),
	(6000, 'damage_given', Award("Berserker", None, "Most damage given")),
	(2, 'invis_count', Award("Hollow Man", None, "Most often picked up Invisibility")),
	(2, 'regen_count', Award("Snake Blood", None, "Most often picked up Regen")),
	(3, 'mega_health_count', Award("Mega Man", None, "Most often picked up Mega Health")),
	(2, 'quad_count', Award("Demolition Man", None, "Most often picked up Quad")),
	(2, 'haste_count', Award("Speeder", None, "Most often picked up Haste")),
	(2, 'medkit_count', Award("The Doc", None, "Most often picked up the Medikit")),
	(5, 'flag_caps', Award("Flag Runner", None, "Most flag captures")),
	(11, 'flag_returns', Award("Clucking Hen", None, "Most flag returns")),
#(5, 'flag_assist_returns', Award("JIT Clucking Hen", None, "Most flag assist returns")),
	(10, 'flag_carrier_kills', Award("Headhunter", None, "Most flag carrier kills")),
	(3, 'suicides', Award("Suicide Bunny", None, "Most suicides")),
	(3, 'team_kills', Award("Frag is Frag", None, "Most team kills")),
	(250, 'team_damage_given', Award("Colorblind", None, "Most team damage given")),
	(5, 'base_defends', Award("Housekeeper", None, "Most base defends")),
	(5, 'flag_defends', Award("Flag Paladin", None, "Most flag defends")),
	(11, 'carrier_defends', Award("Carrier Paladin", None, "Most carrier defends")),
	(100, 'chat_length', Award("Chatterbox", None, "Most chatted characters")),
	(8, 'kill_streak', Award("Killing Spree", None, "highest kill streak")),
	(7, 'death_streak', Award("Frustrated Dead", None, "highest death streak")),
	(2, 'cap_streak', Award("Capture King", None, "highest cap streak")),
	(2.01, 'dmg_kill_ratio', Award("Hard Worker", None, "Most damage per kill")),
	(0, 'sudden_death_decider', Award("Sudden Death Decider", None, "Final cap in sudden death overtime")),
]
## maximum, attribute name, award
_ULTIMATE_MAX = 1000000
_MIN_AWARDS = [
	(1.5, 'dmg_kill_ratio', Award("Lucky Bastard", None, "Least damage per kill")),
	(99, 'team_damage_given', Award("Friendliest Fire", None, "Least team damage")),
	(10, 'death_count', Award("Survivor", None, "Least deaths")),
]
## minimum, weapon, weapon attribute, award
_MAX_WEAPONS = [
	(3, 'gauntlet', 'kills', Award("Pummel King", None, "Most kills with gauntlet")),
	(4, 'gauntlet', 'shots', Award("Close Combateer", None, "Most shots with gauntlet")),
	(10, 'shotgun', 'kills', Award("Hot Shot", None, "Most kills with shotgun")),
	(400, 'shotgun', 'shots', Award("Pumping Player", None, "Most shots with shotgun")),
	(400, 'machinegun', 'shots', Award("Trigger Happy", None, "Most shots with machine gun")),
	(10, 'machinegun', 'kills', Award("Brave Soldier", None, "Most kills with machine gun")),
	(110, 'rocketlauncher', 'shots', Award("Rocketeer", None, "Most shots with rocket launcher")),
	(0.45, 'rocketlauncher', 'hitrate', Award("Cruise Missile", None, "Best hitrate with rocket launcher")),
	(4, 'grenadelauncher', 'kills', Award("Bomber", None, "Most kills with grenade launcher")),
	(0.2, 'grenadelauncher', 'hitrate', Award("Trajectorist", None, "best hitrate with grenade launcher")),
	(1500, 'lightninggun', 'shots', Award("High Voltage", None, "Most shots with lightning gun")),
	(20, 'lightninggun', 'kills', Award("Electrocutioner", None, "Most kills with lightning gun")),
	(20, 'plasmagun', 'hitrate', Award("Plasma hitter", None, "best hitrate with plasma gun")),
	(200, 'plasmagun', 'shots', Award("Plasmatic", None, "Most shots with plasma gun")),
	(10, 'railgun', 'kills', Award("Sniper", None, "Most kills with railgun")),
	(100, 'railgun', 'shots', Award("Railfreak", None, "Most shots with railgun")),
	(0.45, 'railgun', 'hitrate', Award("Railmaster", None, "Best hitrate with railgun")),
	(0, 'teleport', 'kills', Award("Telefragger", None, "Most kills by teleport")),
]
_META_AWARDS = [
	(('Sniper', 'Railfreak', 'Railmaster'), Award("Rail king", None, "Highest hitrate, most kills and most shots with railgun")),
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


