#!/bin/bash

# Install requirements
apt-get update
apt-get install -y \
	git unzip make \
	libusb-1.0 cmake build-essential libpulse-dev libx11-dev \
	python3 python3-pip python3-venv

# Temp directory
mkdir -p .tmp
rm -rf .tmp/*

# Install RTL-SDR
install_sdr() {
	cd .tmp
	git clone git://git.osmocom.org/RTL-SDR.git
	cd RTL-SDR
	mkdir build
	cd build
	cmake ../ -DINSTALL_UDEV_RULES=ON
	make
	make install
	ldconfig

	# Blacklist drivers to prevent kernel from claiming them
	BLACKLIST=/etc/modprobe.d/raspi-blacklist.conf
	if ! cat $BLACKLIST &> /dev/null
	then
		BLACKLIST=/etc/modprobe.d/blacklist.conf
	fi

	DRIVERS="dvb_usb_rtl28xxu rtl2832 rtl2830"

	for DRIVER in $DRIVERS
	do
		if ! cat $BLACKLIST | grep $DRIVER &> /dev/null
		then
			print 2 "Adding $DRIVER to the blacklist..."
			echo "blacklist $DRIVER" | tee -a $BLACKLIST
		else
			print 3 "$DRIVER already on blacklist."
		fi
	done

	echo "Installation of RTL-SDR complete!"

	cd ../../../
}

# Install Multimon
install_mng() {
	cd .tmp
	wget https://github.com/EliasOenal/multimon-ng/archive/1.1.9.zip
	unzip 1.1.9.zip
	cd multimon-ng-1.1.9
	mkdir build
	cd build
	cmake ../
	make
	make install
	cd ../../../
}

# Check RTL-SDR
if ! command -v rtl_test &> /dev/null
then
	read -p "RTL-SDR not found! Install? " yn
	case $yn in
		[Yy]* ) install_sdr; break;;
		* ) ;;
	esac
else
	echo "RTL-SDR already installed!"
fi

# Check Multimon
if ! command -v multimon-ng &> /dev/null
then
	read -p "Multimon-NG not found! Install? " yn
	case $yn in
		[Yy]* ) install_mng; break;;
		* ) ;;
	esac
else
	echo "Multimon-NG already installed!"
fi

# Create python venv
if [ ! -f "venv/bin/python" ]; then
	echo "Creating virtual python environment..."
	python -m pip venv venv
	source venv/bin/activate
	echo "Installing / updating packages..."
	python -m pip install -r requirements.txt
fi

# Cleanup
rm -rf .tmp
echo "Installation complete!"
