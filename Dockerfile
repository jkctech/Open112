FROM debian:bullseye

# Install packages
RUN apt-get update && apt install -y \
	python3 python3-pip \
	kmod \
	wget unzip git \
	libusb-1.0-0-dev cmake build-essential libpulse-dev libx11-dev

# Workdir
RUN mkdir /root/open112
WORKDIR "/tmp"

RUN git clone git://git.osmocom.org/rtl-sdr.git && \
		cd rtl-sdr && \
		mkdir build && \
		cd build && \
		cmake ../ -DINSTALL_UDEV_RULES=ON && \
		make && \
		make install && \
		ldconfig

RUN echo "blacklist dvb_usb_rtl28xxu" > /etc/modprobe.d/blacklist.conf
RUN echo "blacklist rtl2832" > /etc/modprobe.d/blacklist.conf
RUN echo "blacklist rtl2830" > /etc/modprobe.d/blacklist.conf

RUN wget https://github.com/EliasOenal/multimon-ng/archive/1.1.9.zip && \
	unzip 1.1.9.zip && \
	cd multimon-ng-1.1.9 && \
	mkdir build && \
	cd build && \
	cmake ../ && \
	make && \
	make install

CMD ["bash"]
