import sys
import os

from colored import fg

# Header settings
lines = [
	" █████╗ ██████╗ ███████╗███╗  ██╗  ███╗    ███╗  ██████╗ ",
	"██╔══██╗██╔══██╗██╔════╝████╗ ██║ ████║   ████║  ╚════██╗",
	"██║  ██║██████╔╝█████╗  ██╔██╗██║██╔██║  ██╔██║    ███╔═╝",
	"██║  ██║██╔═══╝ ██╔══╝  ██║╚████║╚═╝██║  ╚═╝██║  ██╔══╝  ",
	"╚█████╔╝██║     ███████╗██║ ╚███║███████╗███████╗███████╗",
	" ╚════╝ ╚═╝     ╚══════╝╚═╝  ╚══╝╚══════╝╚══════╝╚══════╝"
]
xpadd = 4
ypadd = 2

width = len(lines[0]) + xpadd * 2 + 2

def printheader(version):
	# Clear screen
	if os.name == "nt":
		os.system("cls")
	else:
		os.system("clear")

	# Print border top
	print(fg('white') + "╔", end="")
	print("═" * (len(lines[0]) + xpadd * 2), end="")
	print("╗")

	# Print border top padding
	for i in range(ypadd):
		print("║", end="")
		print(" " * (len(lines[0]) + xpadd * 2), end="")
		print("║")

	# Print header lines
	for line in lines:
		print("║" + " " * xpadd, end="")
		print(fg('magenta') + line + fg('white'), end="")
		print(" " * xpadd + "║")

	# Print bottom padding
	for i in range(ypadd - 1):
		print("║", end="")
		print(" " * (len(lines[0]) + xpadd * 2), end="")
		print("║")

	# Print credit line
	credit = "By: JKCTech"
	version = "Version: " + version

	print("║", end="")
	print(" " + credit, end="")
	print(" " * (len(lines[0]) + xpadd * 2 - len(version) - len(credit) - 2), end="")
	print(version, end=" ")
	print("║")
	
	# Print border bottom
	print("╚", end="")
	print("═" * (len(lines[0]) + xpadd * 2), end="")
	print("╝")
