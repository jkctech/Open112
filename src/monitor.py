import os
import datetime
import asyncio
import shutil
import json

import queue as Queue
from utils.Radio import Radio

os.system('color')
from colored import fg

# Version information
__version__ = "2.3.0"

# Variables
settings = None
queue = None
radio = None

async def radioloop():
	global queue, radio, settings

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
		await asyncio.sleep(0.2)

async def queuechecker():
	global queue

	while True:
		alert = queue.get()



		queue.task_done()

		await asyncio.sleep(0.2)

# Main async loop
async def main():
	try:
		await asyncio.gather(
			radioloop(),
			queuechecker()
		)

	except KeyboardInterrupt:
		print(fg('red') + "\nClosed by user.")

	finally:
		radio.stop()
		print(fg('white'))

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

	# Run all tasks
	asyncio.run(main())
