import openpyxl
import sys

from termcolor import colored

# Arguments (Get XLSX file)
args = sys.argv
if len(args) != 2:
	print(colored("Please provide the capcode XLSX file only.", "red"))

# Open file
workbook = openpyxl.load_workbook(args[1], read_only=True, data_only=True)

# Iterate over tabs
for sheet in workbook.worksheets:
	
	# Region number SHOULD be here
	# If not, this is a different sheet.
	regio = sheet.title[:2]
	if (regio.isnumeric()):
		regio = int(regio)
		print(regio)
