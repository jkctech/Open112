#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "Please run as root: sudo" $0
	exit
fi

cd ..

cp src/open112.service /etc/systemd/system/open112.service
sed -i 's@{PWD}@'"$PWD"'@' /etc/systemd/system/open112.service
systemctl daemon-reload
systemctl enable open112
echo "Open112 has been enabled at startup!"
