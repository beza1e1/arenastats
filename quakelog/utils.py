infinity = float("infinity")

def slugify(name):
	name = name.replace(" ", "_")
	for char in ".;!?$()":
		name = name.replace(char, "")
	return name.lower()

class Toggler:
	def __init__(self, *items):
		self.items = list(items)
	def __str__(self):
		i = self.items.pop(0)
		self.items.append(i) # move to the back
		return i

def reduce_len(lst, new_len):
	group_len = max(1, len(lst) / new_len)
	res = list()
	i = 0
	sum = 0
	for e in lst:
		if i == group_len:
			res.append(sum / group_len)
			sum = e
			i = 1
		else:
			sum += e
			i += 1
	if i > 0:
		res.append(sum / i)
	return res

def normalize(lst, max):
	def norm(e):
		return int(100 * (e / max))
	return [norm(e) for e in lst]

def googlechart_url(**kwargs):
	url = "http://chart.apis.google.com/chart?"
	args = list()
	type = kwargs.pop('type', 'lc')
	args.append('cht=' + type)
	height = kwargs.pop('height', 200)
	width  = kwargs.pop('width', 400)
	args.append('chs=%dx%d' % (width, height))
	data = kwargs.pop('data', [[1,2,3,4,3], [2,4,3,1,2]])
	data = [reduce_len(d, 12) for d in data]
	maxd = 0
	mind = 0
	for line in data:
		for d in line:
			maxd = max(maxd, d)
			mind = min(mind, d)
	data = [normalize(d, maxd) for d in data]
	steps = maxd / 10
	args.append('chxt=y')
	args.append('chxr=0,0,%.3f,%.3f' % (maxd, steps))
	colors = kwargs.pop('colors', "FF0000 00FF00 0000CC FF00FF 00FFFF 8888FF 880000 008800 000088 888888 339999 3399FF 9933CC FF6633 996600 880088".split(" "))
	colors = colors[:len(data)]
	def _data_line(lst):
		return ",".join(map(str, lst))
	data = "|".join(map(_data_line, data))
	args.append('chd=t:' + data)
	legend = kwargs.pop('legend', ['red', 'blue'])
	args.append('chdl=' + "|".join(legend))
	args.append('chco=' + ",".join(colors))

	for k,v in kwargs.items():
		args.append('%s=%s' % (k, v))
	args = "&".join(args)
	return url + args

