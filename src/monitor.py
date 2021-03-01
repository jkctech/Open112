import os
import subprocess
import fcntl
import time
import datetime

from termcolor import colored

command = "rtl_fm -f 169.65M -M fm -s 22050 | multimon-ng -q -a FLEX -t raw /dev/stdin"

if __name__ == "__main__":
	try:
		# Create datastream from demodulator
		pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)

		# Make subprocess non-blocking
		fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

		while True:
			# If this is None, the process is closed
			if pipe.poll() != None:
				print(colored("Could not claim radio.", "red"))
				exit(3)

			# Read single line and make into string from bytestring
			line = pipe.stdout.readline().decode("utf-8").strip()

			# If there's something to read...
			if len(line) > 0:
				blocks = line.split("|")

				# Check if line is an actual alert
				if blocks[6] == "ALN":
					# Make list of capcodes and put in the first one
					capcodes = [blocks[3]]
					
					# Only select interesting part: Message (And capcodes if applicable)
					data = blocks[8:]

					# Final selecting of data
					if len(data) > 1:
						# Last element it alert
						alert = data.pop(-1)

						# Append the rest to capcodes
						capcodes = capcodes + data
					else:
						# If only an alert, save it
						alert = data[0]

					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Print alert
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "red"), end=" ")
					print(alert)

					# Print capcodes
					for code in capcodes:
						print(colored("\t" + code, "cyan"))
			
			# Only read every second
			time.sleep(1)
	
	except KeyboardInterrupt:
		print(colored("\nClosed by user.", "red"))
		exit(0)
