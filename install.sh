#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;92m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Sexy print function
print () {
	if [ $1 == 0 ]; then
		printf "${GREEN}$2${NC}\n"
	elif [ $1 == 1 ]; then
		printf "${RED}$2${NC}\n"
	elif [ $1 == 2 ]; then
		printf "${CYAN}$2${NC}\n"
	elif [ $1 == 3 ]; then
		printf "${YELLOW}$2${NC}\n"
	fi
}

print 0 "Installing Open112..."

# Temp directory
mkdir -p .tmp
rm -rf .tmp/*

# Install requirements
sudo apt-get update
sudo apt-get install -y git libusb-1.0 cmake build-essential libpulse-dev libx11-dev

# Install SDR Driver if needed
if ! command -v rtl_test &> /dev/null
then
	print 2 "Installing RTL-SDR Driver..."
    cd .tmp
	git clone git://git.osmocom.org/rtl-sdr.git
	cd rtl-sdr
	mkdir build
	cd build
	cmake ../ -DINSTALL_UDEV_RULES=ON
	make
	sudo make install
	sudo ldconfig
	cd ../../../
	print 0 "Done!"
else
	print 3 "RTL-SDR Driver already installed!"
fi

# Select Blacklist
print 2 "Selecting blacklist..."
BLACKLIST=/etc/modprobe.d/raspi-blacklist.conf
if ! cat $BLACKLIST &> /dev/null
then
	BLACKLIST=/etc/modprobe.d/blacklist.conf
fi
print 0 "Blacklist: $BLACKLIST"

# Blacklist drivers
DRIVERS="dvb_usb_rtl28xxu rtl2832 rtl2830"

for DRIVER in $DRIVERS
do
	if ! cat $BLACKLIST | grep $DRIVER &> /dev/null
	then
		print 2 "Adding $DRIVER to the blacklist..."
		echo "blacklist $DRIVER" | sudo tee -a $BLACKLIST
	else
		print 3 "$DRIVER already on blacklist."
	fi
done

# Download & install specific Multimon-NG version
if ! command -v multimon-ng &> /dev/null
then
	print 2 "Installing Multimon-NG..."
	cd .tmp
	wget https://github.com/EliasOenal/multimon-ng/archive/1.1.9.zip
	unzip 1.1.9.zip
	cd multimon-ng-1.1.9
	mkdir build
	cd build
	cmake ../
	make
	sudo make install
	cd ../../../
	print 0 "Done!"
else
	print 3 "Multimon-NG already installed!"
fi

print 2 "Cleaning up..."
rm -rf .tmp

print 0 "Installation complete!"
