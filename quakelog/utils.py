def slugify(name):
	name = name.replace(" ", "_")
	for char in ".;!?$()":
		name = name.replace(char, "")
	return name
