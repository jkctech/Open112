import argparse

argv = None

def init():
	global argv

	parser = argparse.ArgumentParser()

	parser.add_argument("-f", "--feed", action="store_true", help="Feed your data to 112Centraal. (Requires -k)", default=False)
	parser.add_argument("-k", "--key", help="Your 112Centraal API key.")
	parser.add_argument("-nc", "--nocapcodes", action="store_true", help="Don't print capcodes to the screen.")
	parser.add_argument("-ld", "--loopdelay", type=int, default=1, help="Time between reads from the radio pipe.")
	parser.add_argument("-t", "--timeout", type=int, default=600, help="Amount of loops before a radio death will be triggered.")
	parser.add_argument("-r", "--retries", type=int, default=5, help="Amount of retries on radio death.")
	parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging mode.")

	argv = parser.parse_args()
