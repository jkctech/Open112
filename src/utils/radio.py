import subprocess
import fcntl
import time
import os
import signal

from termcolor import colored

_command = "rtl_fm -f 169.65M -M fm -s 22050 | multimon-ng -q -a FLEX -t raw -"
_restarts = 5

pipe = None
pid = 0

# Attempt to start the radio
def start():
	global pipe, pid

	print(colored("Starting radio...", "cyan"))

	# Do 5 attempts to start the radio
	for i in range(_restarts):
		# Print attempt
		if i > 0:
			print(colored("Attempt ", i + 1, "red"))
			time.sleep(i - (i > 0))

		# Create datastream from demodulator
		pipe = subprocess.Popen(_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)

		# Make subprocess non-blocking
		fcntl.fcntl(pipe.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

		time.sleep(1)

		# If cannot open:
		if pipe.poll() != None:
			# Attempt to kill and wait a little (Longer every attemp)
			stop()
		else:
			# rtl_fm pid is shell pid + 1
			pid = pipe.pid + 1
			print(colored("Radio active (PID: {})".format(pid), "green"))
			return True

	# Could not start
	raise Exception("Could not start radio after {} attempts.".format(_restarts))

# Stop the radio if applicable
def stop():
	global pipe

	if pipe != None:
		os.kill(pid, signal.SIGKILL)
		pipe.kill()
		pipe = None

# Perform a stop and start
def restart():
	stop()
	time.sleep(1)
	start()