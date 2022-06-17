import os
import datetime
import json
from subprocess import TimeoutExpired
import time
import threading
import queue as Queue

from shutil import copyfile
from utils import header
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
last = datetime.datetime.now()

def radioloop():
	global queue, radio, settings, last

	while True:

		# Start radio
		print(fg('cyan') + "Starting radio...")
		radio.start()
		print(fg('green') + "Radio running!", fg('white') + "(PID: {})".format(radio.pid))

		try:
			while radio.pipe.stdout != None:
				line = radio.pipe.stdout.readline().decode("utf-8").strip()

				# If there's something to read...
				if len(line) > 0:
					blocks = line.split("|")

					# Check if line is an actual alert
					if blocks[6] == "ALN":
						# Reset last
						last = datetime.datetime.now()

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
						if settings['feeding'] != True:
							try:
								queue.put(
									{
										"message": message,
										"capcodes": capcodes,
										"time": now
									}
								)
							except Queue.Full:
								pass

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

		# Specific error is caused when the radio is killed, so we pass on it
		except AttributeError:
			pass

		# Report other errors...
		except Exception as e:
			print(fg('red') + "ERROR: " + fg('white') + str(e))

		# Housekeeping
		finally:
			print(fg('white'))
		
		print(fg('yellow') + "Radio has terminated..." + fg('white'))
		print()

def queuechecker():
	global queue, settings

	# If not feeding, stop
	if settings['feeding'] != True:
		return

	feeder = Feeder()

	while True:
		try:
			# Get message from queue
			alert = queue.get(timeout=0.2)

			# Attempt to feed and save result
			result = feeder.feed(alert)

			# Mark as done anyway
			queue.task_done()

			# If failed, store for later, just in case
			if result == False:
				queue.put(alert)

			time.sleep(0.2)

		# If empty, we are on schedule :)
		except Queue.Empty:
			pass

		# Max queuesize just in case, if full on re-insert, just do nothing
		except Queue.Full:
			pass

# Watches if radio receives message in x time
# MKOB Den Bosch sends out a ping every 5 minutes which is very useful
def watcher():
	global last, radio

	while True:
		# Check timeout
		if last + datetime.timedelta(seconds=settings['radio']['timeout']) < datetime.datetime.now():
			print(fg('yellow') + "\nWARNING: " + fg('white') + "Radio timed out, terminating...")
			
			# Kill & reset timer
			radio.stop()
			last = datetime.datetime.now()

		time.sleep(1)

if __name__ == "__main__":
	try:
		# Header
		header.printheader()
		print()

		# Parse settings
		if not os.path.exists("config.json"):
			copyfile("config_default.json", "config.json")
		with open("config.json", "r") as f:
			settings = json.load(f)

		# Build radio
		radio = Radio(
			device_id=settings['radio']['device_id'],
			gain=settings['radio']['gain']
		)

		# Start queue
		if settings['feeding'] != True:
			queue = Queue.Queue(maxsize=512)

		# Function we want to thread
		targets = [
			radioloop,
			queuechecker,
			watcher
		]

		# Create all threads and start
		threads = []
		for t in targets:
			th = threading.Thread(target=t, daemon=True)
			threads.append(th)
			th.start()

		# Keep-alive
		while True in [t.is_alive() for t in threads]:
			time.sleep(0.1)

	# Housekeeping		
	except KeyboardInterrupt:
		print(fg('red') + "\nAborted by user.")

	finally:
		print(fg('white'))
