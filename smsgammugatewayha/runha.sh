#!/usr/bin/env bashio

port=$(bashio::addon.port 5000)
device=$(bashio::config 'device')
nomodem=$(bashio::config 'nomodem')

echo $port
echo $device
echo $nomodem

echo [gammu1] > gammu.config
echo device = $device >> gammu.config
echo 'name = SIM7600X-4G-HAT' >> gammu.config
echo 'connection = at' >> gammu.config

if [ $nomodem -eq 1 ]
then
  python runnomodem.py
else
  python run.py
fi
