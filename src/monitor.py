import os
import time
import datetime

os.system('color')
from termcolor import colored

from utils import args
from utils.Radio import Radio

# Version information
__version__ = "2.3.0"

if __name__ == "__main__":
	from utils import header

	# Header
	header.printheader()
	print()

	# Get runtime args
	args.init()

	# Build radio
	radio = Radio(restarts=args.argv.retries)

	try:
		# Start radio
		print(colored("Starting radio...", "cyan"))
		radio.start()
		print(colored("Radio running!", "green"), colored("(PID: {})".format(radio.pid), "white"))

		while True:
			line = radio.pipe.stdout.readline().decode("utf-8").strip()

			# If there's something to read...
			if len(line) > 0:
				blocks = line.split("|")

				# Check if line is an actual alert
				if blocks[6] == "ALN":
					# Make list of capcodes
					capcodes = [blocks[3]]
					if len(blocks) > 9:
						capcodes += blocks[8:-1]
					
					# Select actual message
					message = blocks[-1]

					# Remove leading 0's in capcodes
					for i in range(len(capcodes)):
						capcodes[i] = capcodes[i][2:]

					# Get current timestamp
					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Print alert
					print()
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "red"), end=" ")
					print(colored(message, "white"))
					
					i = 0
					print("\t", end="")
					for code in capcodes:
						print(colored(code, "cyan"), end=" ")
						i += 1
						if i == 5:
							print("\n\t", end="")
							i = 0
					if i != 0:
						print()

			# Delay for stability
			time.sleep(0.2)
	
	# Closed intentionally
	except KeyboardInterrupt:
		print(colored("\nClosed by user.", "red"))
	
	# Wait for radio to stop
	finally:
		radio.stop()
		pass
