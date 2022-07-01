import requests
import time

class Feeder:
	endpoints = [
		"https://api.112centraal.nl/post/insert/"
	]

	def __init__(self, version, apikey, endpoints=[]):
		self.version = version
		self.endpoints += endpoints
		self.apikey = apikey

	def feed(self, msgobject):
		data = {
			"message": msgobject['message'],
			"capcodes": ",".join(msgobject['capcodes']),
			"timestamp": int(msgobject['timestamp']),
			"sent": int(time.time()),
			"version": self.version
		}

		headers = {
			'Content-type': 'application/x-www-form-urlencoded'
		}

		for i in range(0, len(self.endpoints)):
			# If feeding 112centraal and no apikey present, skip
			if i == 0 and len(self.apikey) == 0:
				continue

			# Add apikey if 112centraal
			endpoint = self.endpoints[i]
			if i == 0:
				data['apikey'] = self.apikey

			# Silently fail
			try:
				requests.post(
					endpoint,
					data=data,
					headers=headers,
					timeout=(2, 10)
				)
			except Exception:
				pass
			
			if i == 0:
				del data['apikey']
