# Convert discipline ID to color for in terminal
def disciplineColor(discipline):
	if discipline in [1, 11, 12]:
		msgcolor = "white"
	elif discipline in [2, 14]:
		msgcolor = "blue"
	elif discipline in [3]:
		msgcolor = "red"
	elif discipline in [4, 9, 10, 13]:
		msgcolor = "yellow"
	elif discipline in [5]:
		msgcolor = "magenta"
	elif discipline in [6, 7, 8]:
		msgcolor = "green"
	else:
		msgcolor = "grey"
	return msgcolor

# Convert discipline ID to name string
def disciplineString(discipline):
	disciplines = [
		"Onbekend",
		"Politie",
		"Brandweer",
		"Ambulance",
		"Traumateam",
		"Kustwacht",
		"KNRM",
		"Reddingbrigade",
		"DARES",
		"SIGMA",
		"Meldkamer",
		"Brugbediening",
		"Rode Kruis",
		"Rijkswaterstaat",
	]
	return disciplines[discipline - 1]