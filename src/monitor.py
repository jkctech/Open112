import os
import subprocess
import fcntl
import time
import datetime
import argparse

from termcolor import colored

from Atlanet import capinfo

# Version information
__version__ = "2.0.0"

# Prevent circular import on header
if __name__ == "__main__":
	from utils import header

command = "rtl_fm -f 169.65M -M fm -s 22050 | multimon-ng -q -a FLEX -t raw /dev/stdin"

if __name__ == "__main__":
	# Header
	header.printheader()
	print()

	# Argparser
	parser = argparse.ArgumentParser()

	parser.add_argument("-f", "--feed", action="store_true", help="Feed your data to 112Centraal. (Requires -k)", default=False)
	parser.add_argument("-k", "--key", help="Your 112Centraal API key.")
	parser.add_argument("-nc", "--nocapcodes", action="store_true", help="Don't print capcodes to the screen.")

	args = parser.parse_args()

	try:
		print("=" * header.width)
		# Attempt Feeding
		if args.feed:
			# If no key given, error out
			if args.key == None:
				raise Exception("Feeding requires an API key.")
			
			# Only import when needed
			from Atlanet import Atlanet

			# Sign on to the 112Centraal Network
			print(colored("Attempting to connect to 112Centraal:", "cyan"), end=" ")
			feed = Atlanet(args.key)

			# Invalid key or connection error
			logon = feed.setStatus("ONLINE")
			if logon == False:
				args.feed = False
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
		print("=" * header.width)

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
					message = blocks[6]

					# Get current timestamp
					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Remove leading 0's in capcodes
					for i in range(len(capcodes)):
						capcodes[i] = capcodes[i][2:]

					# Feed data if needed
					result = False
					capdata = False
					if args.feed:
						result = feed.send(message, capcodes)

						if result != False and "capcodes" in result['data']:
							capdata = result['data']['capcodes']
					
					# Set message color
					msgcolor = "white"
					if result != False and "result" in result and len(result['result']) > 0:
						alert = result['result'][0]
						if alert == False:
							msgcolor = "grey"
						else:
							msgcolor = capinfo.disciplineColor(alert['discipline'])

					# Print alert
					print()
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "grey"), end=" ")
					print(colored(message, msgcolor))

					# Print capcodes
					if args.nocapcodes == False:
						# Print capcodes in feeding mode
						if capdata != False:
							# Find longest placename
							maxlen = 10
							for code in capdata:
								code = capdata[code]

								if code['plaats'] == None:
									code['plaats'] = "Onbekend"

								if len(code['plaats']) > maxlen:
									maxlen = len(code['plaats'])
							maxlen += 2

							# Loop over codes and print
							for code in capcodes:
								print(colored("\t" + code, "cyan"), end=" ")

								if capdata != False and code in capdata:
									capcode = capdata[code]
									discipline = capinfo.disciplineString(capcode['discipline'])
									print(colored(discipline, capinfo.disciplineColor(capcode['discipline'])) + " " * (16 - len(discipline)), end=" ")
									print(capcode['plaats'] + " " * (maxlen - len(capcode['plaats'])), end=" ")
									print(capcode['description'])
								else:
									print("Onbekend")
						
						# Print in non-feeding mode
						else:
							i = 0
							print("\t", end="")
							for code in capcodes:
								print(colored(code, "cyan"), end=" ")
								i += 1
								if i == 8:
									print()
									i = 0
							if i != 0:
								print()

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
	
	# Wait for radio to stop
	finally:
		time.sleep(3)
