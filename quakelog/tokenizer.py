from datetime import datetime

class GameEvent:
	game_start = False
	game_end = False # end by game rules
	game_destroy = False # end by server
	def __init__(self, sline):
		self.time = -1
		self.line_count = -1
		self.rest_of_line = ' '.join(sline)
	def _parse_backslash_info(self, info, expand_dict):
		info = info.split('\\')
		key = None
		for i in info:
			if key:
				setattr(self, key, i)
				key = None
			else:
				key = expand_dict.get(i, i)

class NoEvent(GameEvent):
	pass

class InitGame(GameEvent):
	game_start = True
	def __init__(self, sline):
		line = " ".join(sline)
		self._parse_backslash_info(line.strip(), {})

class ShutdownGame(GameEvent):
	game_destroy = True
	
class EndGame(GameEvent):
	game_end = True

class Chat(GameEvent):
	def __init__(self, sline):
		line = " ".join(sline)
		self.nick = line[:line.index(":")]
		self.message = line[line.index(":")+1:].strip()

_PLAYER_KEY_EXPAND = {
	'n': 'nick',
	't': 'team_id',
	'hmodel': 'head_model',
}
class PlayerinfoChange(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])
		infostr = " ".join(sline[1:])
		self._parse_backslash_info(infostr, _PLAYER_KEY_EXPAND)

class NewClient(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class KillClient(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class Kill(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])
		self.victim_id = int(sline[1])
		assert sline[2].endswith(":")
		self.some_number = int(sline[2][:-1]) # TODO
		self.weapon_number = int(sline[-1].strip())
		assert sline[-3] == "by"
		self.weapon_description = sline[-2]
		self.msg = " ".join(sline[3:])
	
class ItemPickup(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])
		self.item = sline[1].strip()

class FlagPickup(GameEvent):
	def __init__(self, sline):
		self.player_number = int(sline[0])

class FlagReturn(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class FlagCapture(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class FlagDefend(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class BaseDefend(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class CarrierDefend(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class FlagAssistReturn(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class FlagAssistFrag(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class FlagCarrierKill(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])

class TeamScore(GameEvent):
	def __init__(self, sline):
		self.team_id = int(sline[0])
		self.capture_count = int(sline[1])

class Score(GameEvent):
	def __init__(self, sline):
		line = " ".join(sline)
		self.score = int(sline[0])
		self.client_id = int(line.split('client:')[-1].strip().split(' ')[0])
		self.nick = sline[-1].strip()

class TeamName(GameEvent):
	def __init__(self, sline):
		self.team_id = int(sline[0])
		self.name = sline[1].strip()

class WeaponStats(GameEvent):
	def __init__(self, sline):
		self.client_id = int(sline[0])
		self.stats = dict()
		for stat in sline[1:]:
			stat = stat.split(":")
			self.stats[stat[0]] = map(int, stat[1:])

class ServerTime(GameEvent):
	def __init__(self, sline):
		self.timestamp = sline[0].split("\t")[0]
		self.datetime = datetime.strptime(self.timestamp, "%Y%m%d%H%M%S")

_ACTIONS = {
	'say:': Chat,
	'ClientUserinfoChanged:': PlayerinfoChange,
	'Kill:': Kill,
	'Item:': ItemPickup,
	'Flag_Return:': FlagReturn,
	'Flag_Pickup:': NoEvent, # Tracking of the other events suffices
	'Flag_Capture:': FlagCapture,
	'Team_Score:': TeamScore,
	'Defend_Flag:': FlagDefend,
	'Defend_Base:': BaseDefend,
	'Defend_Carrier:': CarrierDefend,
	'Hurt_Carrier_Defend:': CarrierDefend, #TODO
	'Defend_Hurt_Carrier:': CarrierDefend, #TODO
	'Kill_Carrier:': FlagCarrierKill,
	'Flag_Assist_Return:': FlagAssistReturn,
	'Flag_Assist_Frag:': FlagAssistFrag,
	'InitGame:': InitGame,
	'Game_End:': EndGame,
	'ShutdownGame:': ShutdownGame,
	'ShutdownGame:\n': ShutdownGame,
	'Weapon_Stats:': WeaponStats,
	'score:': Score,
	'TeamScore:': TeamScore,
	'Exit:': EndGame,
	'Warmup:': NoEvent, # there is a ShutdownGame after warm up
	'Game_Start:': NoEvent,
	'Game_Start:\n': NoEvent,
	'ServerTime:': ServerTime,
	'TeamName:': TeamName,
	'ClientDisconnect:': KillClient,
	'ClientConnect:': NewClient,
	'ClientBegin:': NoEvent,
	'------------------------------------------------------------\n': NoEvent,
	'Warmup:\n': NoEvent,
	'tell:': NoEvent,
	'sayteam:': NoEvent,
}

def _parse_line(line, line_count):
	line = line.replace(':\t', ': ')
	sline = line.split(' ')
	time = -1
	if len(sline) == 0:
		return
	try:
		time = float(sline[0])
	except ValueError:
		return
	AC = _ACTIONS.get(sline[1], None)
	if not AC:
		return
	a = AC(sline[2:])
	a.line_count = line_count
	a.time = time
	return a

def tokenize(lines):
	line_count = 1
	for line in lines:
		event = _parse_line(line, line_count)
		if event and not isinstance(event, NoEvent):
			yield event
		line_count += 1
