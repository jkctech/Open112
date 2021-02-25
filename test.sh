#!/bin/bash

# Colors
RED='\033[0;31m'
NC='\033[0m'

# Command to start receiving 112 messages
rtl_fm -f 169.65M -M fm -s 22050 | multimon-ng -q -a FLEX -t raw /dev/stdin

# If not manually aborted:
if [ $? -ne 130 ]
then
	printf "${RED}Error while using the SDR, did you reboot after installing Open112?${NC}\n"
fi
