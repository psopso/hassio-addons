#!/usr/bin/with-contenv bashio
set -e

# Načtení údajů z MQTT service discovery
MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USER=$(bashio::services mqtt "username")
MQTT_PASS=$(bashio::services mqtt "password")

# Příklad výpisu (jen pro ladění, v produkci heslo nevypisujte)
bashio::log.info "Connecting to MQTT at ${MQTT_HOST}:${MQTT_PORT}"

#python3 -u /x728_manager_gpio.py $__BASHIO_SUPERVISOR_TOKEN
