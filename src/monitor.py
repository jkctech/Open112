import os
import subprocess
import fcntl
import time
import datetime
import argparse

from termcolor import colored

command = "rtl_fm -f 169.65M -M fm -s 22050 | multimon-ng -q -a FLEX -t raw /dev/stdin"

def resolveCapcode(capcode):
	database = {
		"0120901": "Lifeliner 1 (Traumahelikopter Mobiel Medisch Team)",
		"1420059": "Lifeliner 2 (Traumahelikopter Mobiel Medisch Team)",
		"0923993": "Lifeliner 3 (Traumahelikopter Mobiel Medisch Team)",
		"2029568": "Groepscode",
		"2029569": "Groepscode",
		"2029570": "Groepscode",
	}

	if capcode in database:
		return database[capcode]
	else:
		return "Onbekend"

if __name__ == "__main__":
	# Argparser
	parser = argparse.ArgumentParser()

	parser.add_argument("-f", "--feed", action="store_true", help="Feed your data to 112Centraal. (Requires -k)", default=False)
	parser.add_argument("-k", "--key", help="Your 112Centraal API key.")
	parser.add_argument("-nc", "--nocapcodes", action="store_true", help="Don't print capcodes to the screen.")
	# parser.add_argument("-nf", "--noflairs", action="store_true", help="Don't print flairs to the screen.")

	args = parser.parse_args()

	try:
		# Feeding
		if args.feed:
			# If no key given, error out
			if args.key == None:
				raise Exception("Feeding requires an API key.")
			
			from Atlanet import Atlanet

			# Sign on to the 112Centraal Network
			feed = Atlanet(args.key)

			# Invalid key or connection error
			if feed.setStatus("ONLINE") == False:
				raise Exception("Could not connect to the 112Centraal network.")
			
			# OK
			print(colored("Feeding to 112Centraal...", "cyan"))
		else:
			print(colored("Not feeding to 112Centraal.\nPlease consider becoming a feeder!", "yellow"))

		# Create datastream from demodulator
		pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)

		# Make subprocess non-blocking
		fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

		while True:
			# If this is None, the process is closed
			if pipe.poll() != None:
				raise Exception("Radio connection closed unexpectedly.")

			# Read single line and make into string from bytestring
			line = pipe.stdout.readline().decode("utf-8").strip()

			# If there's something to read...
			if len(line) > 0:
				blocks = line.split("|")

				# Check if line is an actual alert
				if len(blocks) == 7 and blocks[5] == "ALN":
					# Make list of capcodes
					capcodes = blocks[4].split(" ")
					
					# Select actual message
					alert = blocks[6]

					# Get current timestamp
					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Remove leading 0's in capcodes
					for i in range(len(capcodes)):
						capcodes[i] = capcodes[i][2:]

					# Feed data if needed
					if args.feed:
						result = feed.send(alert, capcodes)
					
					# Set color
					msgcolor = "white"

					if result != False and "result" in result and len(result['result']) > 0:
						result = result['result'][0]

						if result == False:
							msgcolor = "grey"
						elif result['discipline'] in [1, 11, 12]:
							msgcolor = "white"
						elif result['discipline'] in [2, 14]:
							msgcolor = "blue"
						elif result['discipline'] in [3]:
							msgcolor = "red"
						elif result['discipline'] in [4, 9, 10, 13]:
							msgcolor = "yellow"
						elif result['discipline'] in [5]:
							msgcolor = "magenta"
						elif result['discipline'] in [6, 7, 8]:
							msgcolor = "green"

					# Print alert
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "red"), end=" ")
					print(colored(alert, msgcolor))

					# Print capcodes
					if args.nocapcodes == False:
						for code in capcodes:
							print(colored("\t" + code, "cyan"), end=" ")
							print(resolveCapcode(code))
			
			# Only read every second
			time.sleep(1)
	
	# Closed intentionally
	except KeyboardInterrupt:
		print(colored("\nClosed by user.", "red"))
		if args.feed:
			feed.setStatus("OFFLINE")
	
	# Crashed
	except Exception as e:
		if args.feed:
			feed.setStatus("CRASH")
		print(colored(e, "red"))
		raise Exception from e
