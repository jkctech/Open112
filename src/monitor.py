import os
import datetime
import shutil
import json
import time
import threading

import queue as Queue
from utils.Feeder import Feeder
from utils.Radio import Radio

os.system('color')
from colored import fg

# Version information
__version__ = "2.3.0"

# Variables
settings = None
queue = None
radio = None

def radioloop():
	global queue, radio, settings

	try:
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
					now = datetime.datetime.now()

					# Push to queue
					if settings['feeding']:
						queue.put(
							{
								"message": message,
								"capcodes": capcodes,
								"time": now
							}
						)

					# Print alert
					print()
					print(fg('yellow') + now.strftime("%d-%m-%Y %H:%M:%S"), end=" ")
					print(fg('red') + "=>", end=" ")
					print(fg('white') + message)
					
					i = 0
					print("\t", end="")
					for code in capcodes:
						print(fg('cyan') + code, end=" ")
						i += 1
						if i == 5:
							print("\n\t", end="")
							i = 0
					if i != 0:
						print()
					print(fg('white'), end="")

			# Delay for stability
			time.sleep(0.2)

	except KeyboardInterrupt:
		print(fg('red') + "\nClosed by user.")

	finally:
		radio.stop()
		print(fg('white'))

def queuechecker():
	global queue

	feeder = Feeder()

	while True:
		try:
			alert = queue.get(timeout=0.2)

			result = feeder.feed(alert)
	
			queue.task_done()
			if result == False:
				queue.put(alert)
			
			time.sleep(0.2)
		
		except Queue.Empty:
			pass

if __name__ == "__main__":
	from utils import header

	# Header
	header.printheader()
	print()

	# Parse settings
	if not os.path.exists("config.json"):
		shutil.copyfile("config_default.json", "config.json")
	with open("config.json", "r") as f:
		settings = json.load(f)

	# Build radio
	radio = Radio(
		device_id=settings['radio']['device_id'],
		gain=settings['radio']['gain']
	)

	# Start radio
	print(fg('cyan') + "Starting radio...")
	radio.start()
	print(fg('green') + "Radio running!", fg('white') + "(PID: {})".format(radio.pid))

	# Start queue
	queue = Queue.Queue()

	targets = [
		radioloop,
		queuechecker
	]

	# Run all tasks
	threads = []
	for t in targets:
		th = threading.Thread(target=t, daemon=True)
		threads.append(th)
		th.start()

	while True in [t.is_alive() for t in threads]:
		time.sleep(0.05)

