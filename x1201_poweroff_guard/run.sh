#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting X1201 Poweroff Guard"

exec python3 -u /x1201_guard.py