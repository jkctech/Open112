import argparse

argv = None

def init():
	global argv

	parser = argparse.ArgumentParser()

	parser.add_argument("-nf", "--nofeed", action="store_true", help="Disables feeding data to 112Centraal.", default=False)
	parser.add_argument("-r", "--retries", type=int, default=5, help="Amount of retries on radio death.")

	argv = parser.parse_args()
