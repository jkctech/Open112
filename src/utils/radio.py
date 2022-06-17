import subprocess
import time
import os
import psutil
import signal

from utils.Sysinfo import Sysinfo

class Radio:

	def __init__(self, device_id=0, gain="automatic", restarts=5):
		self.pipe = None
		self.pid = 0
		self.gain = gain
		self.device = device_id
		self.sysinfo = Sysinfo()
		self.restarts = restarts

		self.__setCommand()

	# Set correct command depending on OS
	def __setCommand(self):
		if "windows" in self.sysinfo.system:
			self.command = ".\\rtl_fm.exe -f 169.65M -M fm -s 22050 -d {} -g {} | .\\multimon-ng.exe -q -a FLEX -t raw -".format(self.device, self.gain)
		
		elif "linux" in self.sysinfo.system or "darwin" in self.sysinfo.system:
			self.command = "rtl_fm -f 169.65M -M fm -s 22050 -d {} -g {} | multimon-ng -q -a FLEX -t raw -".format(self.device, self.gain)
		
		else:
			raise Exception("Unknown operating system, cannot prepare radio.")

	def start(self):
		if "windows" in self.sysinfo.system:
			os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/../windows")

		for i in range(self.restarts):
			self.pipe = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)

			time.sleep(1)

			# If cannot open:
			if self.pipe.poll() != None:
				self.stop()

			else:
				self.pid = self.pipe.pid
				return

		raise Exception("Could not start radio after {} attempts...".format(self.restarts))

	def stop(self):
		if self.pipe != None:
			# Kill the processes(es) [recursively]
			process = psutil.Process(self.pid)
			for proc in process.children(recursive=True):
				proc.kill()
			process.kill()

			# if "windows" in self.sysinfo.system:
			# 	subprocess.call(['taskkill', '/F', '/T', '/PID',  str(self.pid)])
			# else:
			# 	os.kill(self.pid, signal.SIGKILL)
			self.pipe = None
			self.pid = 0
