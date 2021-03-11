import requests
import json
from termcolor import colored

# Set client status on 112Centraal server.
# ONLINE | OFFLINE | CRASH | UPDATE
def setStatus(self, status):
	# Try sending request to 112Centraal
	try:
		r = requests.post(self.endpoint + "post/status/", data={
			'apikey': self.apikey,
			'status': status,
			'version': self.version
		})
	except Exception as e:
		print(colored("Could not contact server.", "red"))
		print(e)
		return False

	# Parse server answer
	try:
		res = json.loads(r.text)
	except Exception as e:
		print(colored("Invalid response.", "red"))
		print(e)
		return False
	
	# Report errors
	if ('errors' in res):
		for error in res['errors']:
			print(colored("Error: " + str(res['code']) + " - " + error, "red"))
		return False

	# Complete
	return True
