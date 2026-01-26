#!/usr/bin/with-contenv bashio
set -e

# bashio::log.info "Called to power off Home Assistant!!!"

# bashio::host.reboot

python3 -u /run.py $__BASHIO_SUPERVISOR_TOKEN
