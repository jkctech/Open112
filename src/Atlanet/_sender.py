import requests
import json
from termcolor import colored

def send(self, message, capcodes):
	# Send message to server
	try:
		r = requests.post(self.endpoint + "post/insert/", data={
			'apikey': self.apikey,
			'message': message,
			'capcodes': ','.join(capcodes)
		})
	except (Exception) as e:
		print(colored("Could not contact server.", "red"))
		print(e)
		return False

	# Check HTTP code
	if r.status_code != 200:
		print(colored(r.status_code, "red"))
		print(colored(r.reason, "red"))
		return False

	# Process responsedata
	try:
		res = json.loads(r.text)
	except (Exception):
		print(colored("Invalid response.", "red"))
		return False

	if('errors' in res):
		for error in res['errors']:
			print(colored("Error: " + str(res['code']) + " - " + error, "red"))
		return False
	
	return res
