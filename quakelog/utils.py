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
