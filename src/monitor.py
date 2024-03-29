import os
import sys
import datetime
import json
import time
import threading
import queue as Queue

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Version information
__version__ = "2.3.0"

from shutil import copyfile
from utils import header
from utils.Feeder import Feeder
from utils.Radio import Radio
from utils.DisplayServer import DisplayServer

os.system('color')
from colored import fg

# Variables
settings = None
queue = None
radio = None
messages = []
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

				# Skip default messages from rtl_fm
				if line.startswith("Found"):
					line = radio.pipe.stdout.readline().decode("utf-8").strip()
					while line.startswith("Output at") == False:
						line = radio.pipe.stdout.readline().decode("utf-8").strip()
					continue

				# Non-flex usually means error
				if line.startswith("FLEX") == False and line.startswith("Signal") == False:
					print(fg('red') + "Possible error:", fg('white') + line)

				# If there's something to read...
				if len(line) > 0:
					data = Radio.splitblocks(settings['radio']['multimon-version'], line)

					# Check if line is an actual alert
					if data != False and data['aln'] == "ALN":
						# Reset last
						last = datetime.datetime.now()

						# Make list of capcodes
						message = data['message']
						capcodes = data['capcodes']

						# Make capcodes into 7-digit numbers
						for i in range(len(capcodes)):
							capcodes[i] = capcodes[i][-7:]

						# Detect group issues on older Multimon versions
						# https://github.com/EliasOenal/multimon-ng/issues/168
						a = int(capcodes[0])
						missgroup = False
						if a >= 2029568 and a <= 20295783 and len(capcodes) == 1:
							missgroup = True

						now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

						# Push to webserver and keep list limited
						if settings['webserver']['enabled'] == True:
							messages.append({
								"message": message,
								"capcodes": capcodes,
								"time": now,
								"timestamp": time.time()
							})

							if len(messages) > settings['webserver']['messages']:
								messages.pop(0)

						# Push to queue
						if settings['feeder']['enabled'] == True and missgroup == False:
							try:
								queue.put(
									{
										"message": message,
										"capcodes": capcodes,
										"timestamp": time.time()
									},
									block=False
								)
							except Queue.Full:
								pass

						# Print alert
						print()
						print(fg('yellow') + now, end=" ")
						print(fg('red') + "=>", end=" ")
						print(fg('white') + message)

						i = 0
						print("\t", end="")
						for code in capcodes:
							print(fg('cyan') + code, end=" ")
							i += 1
							if i == 5:
								print("\n", end="")
								if len(capcodes) % 5 != 0:
									print("\t", end="")
								i = 0
						print()

						if missgroup:
							print(fg('red'), "\bBroken groupmessage detected >> https://github.com/EliasOenal/multimon-ng/issues/168")

						print(fg('white'), end="")

				# Delay for stability
				time.sleep(0.2)

		# Specific error is caused when the radio is killed, so we pass on it
		except AttributeError:
			pass

		# Report other errors...
		except Exception as e:
			print(fg('red') + "ERROR: " + fg('white') + str(e))
			raise Exception() from e

		# Housekeeping
		finally:
			print(fg('white'))

		print(fg('yellow') + "Radio has terminated..." + fg('white'))
		print()

def queuechecker():
	global queue, settings, __version__

	# Start queue & feeder
	if settings['feeder']['enabled'] == True:
		queue = Queue.Queue(maxsize=512)
		feeder = Feeder(__version__, settings['feeder']['apikey'], settings['feeder']['endpoints'])
	else:
		while True:
			time.sleep(3600)

	# Waiting time variable and max time to prevent eternal waits...
	wtime = 0.2
	maxtime = 60

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
				queue.put(alert, block=False)

				time.sleep(wtime)

				# Increase and limit waiting time on failures
				wtime *= 2
				if wtime >= maxtime:
					wtime = maxtime

			# Make sure we reset waiting time on succeeded feeds
			else:
				wtime = 0.2

		# If empty, we are on schedule :)
		except Queue.Empty:
			pass

		# Max queuesize just in case, if full on re-insert, just do nothing
		except Queue.Full:
			pass

		time.sleep(0.2)

# Watches if radio receives message in x time
# MKOB Den Bosch sends out a ping every 5 minutes which is very useful
def watcher():
	global last, radio

	while True:
		try:
			# Check timeout
			if last + datetime.timedelta(seconds=settings['radio']['timeout']) < datetime.datetime.now():
				print(fg('yellow') + "\nWARNING: " + fg('white') + "Radio timed out, terminating...")

				# Kill & reset timer
				radio.stop()
				last = datetime.datetime.now()

			time.sleep(1)
		except Exception:
			pass

def msglist():
	global messages
	return messages

# Webserver
def displayserver():
	global settings

	if settings['webserver']['enabled'] == True:
		server = DisplayServer(settings['webserver']['hostname'], settings['webserver']['port'], "web", msglist)
		server.serve_forever()

if __name__ == "__main__":
	try:
		# Header
		header.printheader(__version__)
		print()

		# Make copy of default config
		if not os.path.exists("config.json"):
			copyfile("config_default.json", "config.json")

		# Select settings file
		sfile = "config.json"
		if len(sys.argv) >= 2:
			sfile = sys.argv[1]

		# Parse settings
		with open(sfile, "r") as f:
			settings = json.load(f)

		# Build radio
		radio = Radio(
			device_id=settings['radio']['device_id'],
			gain=settings['radio']['gain']
		)

		# Function we want to thread
		targets = [
			radioloop,
			queuechecker,
			watcher,
			displayserver
		]

		# Create all threads and start
		threads = []
		for t in targets:
			th = threading.Thread(target=t, daemon=True)
			threads.append(th)
			th.start()

		# Keep-alive
		while False not in [t.is_alive() for t in threads]:
			time.sleep(0.2)

	# Housekeeping
	except KeyboardInterrupt:
		print(fg('red') + "\nAborted by user.")

	finally:
		radio.stop()
		print(fg('white'))
