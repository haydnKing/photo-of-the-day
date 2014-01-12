#!/bin/bash
mkdir -p ~/.photo_of_the_day
install POTD.py ~/.photo_of_the_day/
install POTD.desktop ~/.config/autostart/

python ~/.photo_of_the_day/POTD.py &
