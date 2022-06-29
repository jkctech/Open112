import subprocess
import time
import psutil

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
			self.command = ".\\windows\\rtl_fm.exe -f 169.65M -M fm -s 22050 -d {} -g {} | .\\windows\\multimon-ng.exe -q -a FLEX -t raw -".format(self.device, self.gain)

		elif "linux" in self.sysinfo.system or "darwin" in self.sysinfo.system:
			self.command = "rtl_fm -f 169.65M -M fm -s 22050 -d {} -g {} | multimon-ng -q -a FLEX -t raw -".format(self.device, self.gain)

		else:
			raise Exception("Unknown operating system, cannot prepare radio.")

	@classmethod
	def splitblocks(cls, version, line):
		blocks = line.split("|")

		if version == "1.1.8":
			return cls.__split_1_1_8(blocks)
		elif version == "1.1.9":
			return cls.__split_1_1_9(blocks)

	@classmethod
	def __split_1_1_8(cls, blocks):
		if len(blocks) < 9:
			return False

		capcodes = [blocks[3]]
		if len(blocks) > 9:
			capcodes += blocks[8:-1]

		return {
			"aln": blocks[6],
			"message": blocks[-1],
			"capcodes": capcodes,
		}

	@classmethod
	def __split_1_1_9(cls, blocks):
		if len(blocks) < 7:
			return False
		return {
			"aln": blocks[5],
			"message": blocks[6],
			"capcodes": blocks[4].split(' '),
		}

	def start(self):
		for i in range(self.restarts):
			self.pipe = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

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
			try:
				# Kill the processes(es) [recursively]
				process = psutil.Process(self.pid)
				for proc in process.children(recursive=True):
					proc.kill()
				process.kill()
			except psutil.NoSuchProcess:
				pass

			# if "windows" in self.sysinfo.system:
			# 	subprocess.call(['taskkill', '/F', '/T', '/PID',  str(self.pid)])
			# else:
			# 	os.kill(self.pid, signal.SIGKILL)
			self.pipe = None
			self.pid = 0
