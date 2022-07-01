#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "Please run as root: sudo" $0
	exit
fi

systemctl disable open112
echo "Open112 has been disabled!"
