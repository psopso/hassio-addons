#!/usr/bin/with-contenv bashio
set -e

# Načtení údajů z MQTT service discovery
export MQTT_HOST=$(bashio::services mqtt "host")
export MQTT_PORT=$(bashio::services mqtt "port")
export MQTT_USERNAME=$(bashio::services mqtt "username")
export MQTT_PASSWORD=$(bashio::services mqtt "password")

# Příklad výpisu (jen pro ladění, v produkci heslo nevypisujte)
# bashio::log.info "Connecting to MQTT at ${MQTT_HOST}:${MQTT_PORT}"

python3 -u /x728_manager_gpio.py $__BASHIO_SUPERVISOR_TOKEN
