# Linux installation

Installing Open112 can be done both manually and automatically.

## By script
Installation of all the required libraries and software can be done by the installer script:

```bash
sudo ./install.sh
```

The installer will:
- Attempt to install all the required apt packages
- Install the RTL-SDR software if needed
- Install Multimon-NG if needed
- Create a virtual environment
- Install the required python-pip packages

Please refer to the <a href="/docs/config.md">Configuration</a> manual to learn how to configure your **Open112** client!

## Manual installation

Installation can be done manually as well and requires a few steps.

### Install apt packages

```bash
sudo apt-get update
sudo apt-get install -y git unzip make libusb-1.0 cmake build-essential libpulse-dev libx11-dev python3 python3-pip python3-venv
```

### Install RTL-SDR
```bash
git clone git://git.osmocom.org/RTL-SDR.git
cd RTL-SDR
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo ldconfig
```

To prevent the Linux kernel from claiming our SDR, we need to blacklist the default drivers. Add the following 3 lines to `/etc/modprobe.d/blacklist.conf` (Or create it if it does not exist already) using `nano` or any other editor: `sudo nano /etc/modprobe.d/blacklist.conf`
```bash
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
```

### Install Multimon-NG

Multimon is the decoder software that makes the raw signals from the SDR into text.

**WARNING:** Multimon-NG 1.1.8 has **known issues** with the FLEX protocol (<a href="/etc/modprobe.d/blacklist.conf" target="_blank">Read More</a>).
Therefore we will **specifically** install the release of Multimon-NG 1.1.9 which is the only confirmed working version. (For now)

```bash
wget https://github.com/EliasOenal/multimon-ng/archive/1.1.9.zip
unzip 1.1.9.zip
cd multimon-ng-1.1.9
mkdir build
cd build
cmake ../
make
sudo make install
```

### Testing the SDR
 
Now we should be able to test our SDR:

```bash
rtl_test
```

Your output should look something like this:

```
Found 1 device(s):
  0:  Generic, RTL2832U, SN: 77771111153705700

Using device 0: Generic RTL2832U
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
Sampling at 2048000 S/s.

Info: This tool will continuously read from the device, and report if
samples get lost. If you observe no further output, everything is fine.

Reading samples in async mode...
```

Leave it running for a few minutes to make sure your SDR is functioning properly. If you see messages like `lost at least 32 bytes` you may have a malfunctioning SDR device.

### Venv & Python-pip packages

To prevent your main Python installation from conflicting / filling up, we will install the required Python packages locally:

```bash
python -m pip install venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

If you ever need to access the virtual environment, run `source venv/bin/activate` from the `Open112` folder.

### Done!

Everything should be ready to go!

Please refer to the <a href="/docs/config.md">Configuration</a> manual to learn how to configure your **Open112** client!
