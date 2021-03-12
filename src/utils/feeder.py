from termcolor import colored

from utils import args

feed = None

def init():
	global feed

	# Attempt Feeding
	if args.argv.feed:
		# If no key given, error out
		if args.argv.key == None:
			raise Exception("Feeding requires an API key.")
		
		# Only import when needed
		from Atlanet import Atlanet

		# Sign on to the 112Centraal Network
		print(colored("Attempting to connect to 112Centraal:", "cyan"), end=" ")
		feed = Atlanet(args.argv.key)

		# Invalid key or connection error
		logon = feed.setStatus("ONLINE")
		if logon == False:
			args.argv.feed = False
			raise Exception("Could not connect to the 112Centraal network.\nPlease check your API key and network connection.")
		
		# OK
		print(colored("[OK]", "green"))

		# Print userdata
		print("Welcome {}!\nYou are currently registered as {} - {}.".format(
			colored(logon['result']['name'], "yellow"),
			colored(logon['result']['description'], "yellow"),
			colored(logon['result']['plaats'], "yellow")
		))
		print(colored("Thank you for being a data feeder!", "green"))

	# Not feeding
	else:
		print(colored("You are currently not feeding to 112Centraal.", "red"))
		print(colored("Please consider becoming a feeder at:", "yellow"), end=" ")
		print(colored("https://112centraal.nl", "green"))
