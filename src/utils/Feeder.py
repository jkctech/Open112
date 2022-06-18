import json
import requests
import time

from utils.Sysinfo import Sysinfo
from os import path
from colored import fg

from monitor import __version__

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

		self.__infofile()

	def feed(self, msgobject):
		data = {
			"message": msgobject,
			"uuid": self.uuid,
			"system ": self.system,
			"version": self.version,
			"release": self.release,
			"node": self.node,
			"machine": self.machine,
			"sent": time.time(),
			"version": __version__
		}

		headers = {
			'content-type': 'application/json'
		}

		try:
			r = requests.post(
				self.ENDPOINT,
				data=json.dumps(data),
				headers=headers,
				timeout=10
			)

			return r

		except Exception:
			return False
	
	def __infotext(self):
		text = ""
		text += "UUID: " + self.uuid + "\n"
		text += "Statistics URL: " + self.ENDPOINT + "stats/" + self.uuid + "\n"
		return text
	
	def __infofile(self):
		if path.exists("feeder_info.txt") == False:
			try:
				with open("feeder_info.txt", "w") as f:
					f.write(self.__infotext())
			except Exception as e:
				print(fg('yellow') + "WARNING: " + fg('white') + "Could not create feeder_info.txt!")
