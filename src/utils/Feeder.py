import json
import requests
import time

from utils.Sysinfo import Sysinfo
from os import path
from colored import fg

from monitor import __version__

class Feeder:
	ENDPOINT = "http://localhost/api/v2/"

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
			"sent": time.time(),
			"version": __version__
		}

		headers = {
			'Content-type': 'application/json'
		}

		try:
			r = requests.post(
				self.ENDPOINT + "insert",
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
		fp = "../feeder_info.txt"
		if path.exists(fp) == False:
			try:
				with open(fp, "w") as f:
					f.write(self.__infotext())
			except Exception as e:
				print(fg('yellow') + "WARNING: " + fg('white') + "Could not create {}!".format(fp))
