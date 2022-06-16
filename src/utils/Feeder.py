import json
import requests

from utils.Sysinfo import Sysinfo

class Feeder:
	ENDPOINT = "https://api.112centraal.nl/v2/"

	def __init__(self):
		sys = Sysinfo()

		self.uuid = sys.getUUID()
		self.system = sys.system
		self.version = sys.version
		self.release = sys.release
		self.node = sys.node
		self.machine = sys.machine
	
	def feed(self, msgobject):
		data = {
			"message": msgobject,
			"uuid": self.uuid,
			"system ": self.system,
			"version": self.version,
			"release": self.release,
			"node": self.node,
			"machine": self.machine
		}

		headers = {
			'content-type': 'application/json'
		}

		try:
			r = requests.post(
				self.ENDPOINT,
				data=json.dumps(data),
				headers=headers
			)

			return r
		
		except Exception:
			return False
