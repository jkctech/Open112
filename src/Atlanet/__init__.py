class Atlanet(object):
	from ._sender import send
	from ._status import setStatus

	def __init__(self, apikey):
		self.apikey = apikey
		self.endpoint = "https://api.112centraal.nl/"
		self.version = "2.0.0"
