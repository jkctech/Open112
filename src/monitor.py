import time
import datetime

from termcolor import colored

from Atlanet import capinfo
from utils import args
from utils import radio
from utils import feeder

# Prevent circular import on header
if __name__ == "__main__":
	from utils import header

# Version information
__version__ = "2.0.0"

if __name__ == "__main__":
	# Header
	header.printheader()
	print()

	# Get runtime args
	args.init()

	# Debug?
	if args.argv.debug:
		print(
			colored(" ===", "red"),
			colored("Debugging mode enabled!", "yellow"),
			colored("===\n", "red")
		)

	# Encapsulate everything in a try so we can catch everything in 1 place
	try:
		# Check feeder
		print("=" * header.width)
		feeder.init()
		print("=" * header.width)

		# Start radio
		print()
		radio.start()

		# Count amount of loops we did not receive anything.
		# MKOB Den Bosch sends out a ping every 5 minutes, so we can presume
		# at least SOMETHING should come through every X time.
		loops = 0

		while True:
			# Check poll on device + Loops
			if radio.pipe.poll() != None or loops > args.argv.timeout:
				print(colored("Radio seems dead, restarting!", "magenta"))
				radio.restart()
				loops = 0

			# Read single line and make into string from bytestring
			line = radio.pipe.stdout.readline().decode("utf-8").strip()

			# If there's something to read...
			if len(line) > 0:
				blocks = line.split("|")

				# Check if line is an actual alert
				if len(blocks) == 7 and blocks[5] == "ALN":
					# Reset loops counter
					loops = 0

					# Make list of capcodes
					capcodes = blocks[4].split(" ")
					
					# Select actual message
					message = blocks[6]

					# Remove leading 0's in capcodes
					for i in range(len(capcodes)):
						capcodes[i] = capcodes[i][2:]

					# Feed data if needed
					result = False
					capdata = False
					if args.argv.feed:
						result = feeder.feed.send(message, capcodes)
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

					# Get current timestamp
					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Print alert
					print()
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "grey"), end=" ")
					print(colored(message, msgcolor))

					# Print capcodes
					if args.argv.nocapcodes == False:
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
					
			# Increment loop counter
			loops += 1

			# Only read every second
			time.sleep(args.argv.loopdelay)
	
	# Closed intentionally
	except KeyboardInterrupt:
		print(colored("\nClosed by user.", "red"))
		if args.argv.feed and feeder.feed != None:
			feeder.feed.setStatus("OFFLINE")
	
	# Crashed
	except Exception as e:
		if args.argv.feed and feeder.feed != None:
			feeder.feed.setStatus("CRASH")
		print(colored(e, "red"))
	
	# Wait for radio to stop
	finally:
		radio.stop()
