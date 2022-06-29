import subprocess
import platform

class Sysinfo:
	
	def __init__(self):
		uname = platform.uname()

		self.system = uname.system.lower()
		self.node = uname.node
		self.release = uname.release
		self.version = uname.version
		self.machine = uname.machine
		self.uuid = self.getUUID()
	
	def getUUID(self):
		# Windows
		if 'windows' in self.system:
			return str(subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()

		# Linux
		elif 'linux' in self.system:
			return subprocess.check_output('cat /etc/machine-id'.split()).decode("utf-8").strip()
			# return subprocess.Popen('hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid'.split())

		# Mac
		elif 'darwin' in self.system:
			result = subprocess.run("system_profiler SPHardwareDataType | grep 'Hardware UUID' | awk '{print $3}'", stdout=subprocess.PIPE, shell=True, check=True)
			return result.stdout.decode("utf-8").strip()
		
		# Unknown
		else:
			raise Exception("Unknown operating system, cannot determine UUID.")
