#!/usr/bin/with-contenv bashio
set -e

echo $MQTT_USERNAME

python3 -u /x728_manager_gpio.py $__BASHIO_SUPERVISOR_TOKEN
