#!/usr/bin/with-contenv bashio

source /venv/bin/activate

echo "I2C test starting..."
python3 test.py
echo
echo "I2Cdetect..."
i2cdetect -y 1

echo
echo "Startuji Yahboom Controller..."
python3 -u /control.py
