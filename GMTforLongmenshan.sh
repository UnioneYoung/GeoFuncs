#!/usr/bin/env -S bash -e
# GMT modern mode bash template
# Date:    2020-03-16T14:42:19
# User:    laputa
# Purpose: Purpose of this script
export GMT_SESSION_NAME=$$	# Set a unique session name
#Basic info below
#dd:mm:ss<E/W/S/N> or <+/->d
#Length unit:1i = 2.54c = 72p, 1c~=28.3p, 1p~=0.035c
mapSize=8i
mecaSize=15p
lowLatitude=27
highLatitude=33
minLongitude=98
maxLongitude=105
resolution=30s
#Don't change below
Region=$minLongitude/$maxLongitude/$lowLatitude/$highLatitude
#Begin here
gmt begin LongMenShanMapOf$resolution png
	echo "Ploting background..."
    gmt grdimage @earth_relief_$resolution -JM$mapSize -R$Region -Bafg -I+d
    echo "Background complete, now CMT..."
    gmt meca /Users/laputa/after2010_CMT_inputGMT.txt -JM$mapSize -R$Region -Sd$mecaSize
gmt end show