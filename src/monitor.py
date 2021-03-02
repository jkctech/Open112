import os
import subprocess
import fcntl
import time
import datetime

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
	try:
		# Create datastream from demodulator
		pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)

		# Make subprocess non-blocking
		fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

		while True:
			# If this is None, the process is closed
			if pipe.poll() != None:
				print(colored("Radio connection closed unexpectedly.", "red"))
				exit(3)

			# Read single line and make into string from bytestring
			line = pipe.stdout.readline().decode("utf-8").strip()

			# If there's something to read...
			if len(line) > 0:
				blocks = line.split("|")

				# Check if line is an actual alert
				if blocks[5] == "ALN":
					# Make list of capcodes
					capcodes = blocks[4].split(" ")
					
					# Select actual message
					alert = blocks[6]

					# Get current timestamp
					now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

					# Remove leading 0's in capcodes
					for i in range(len(capcodes)):
						capcodes[i] = capcodes[i][2:]

					# Print alert
					print(colored(now, "yellow"), end=" ")
					print(colored("=>", "red"), end=" ")
					print(alert)

					# Print capcodes
					for code in capcodes:
						print(colored("\t" + code, "cyan"), end=" ")
						print(resolveCapcode(code))
			
			# Only read every second
			time.sleep(1)
	
	except KeyboardInterrupt:
		print(colored("\nClosed by user.", "red"))
		exit(0)
