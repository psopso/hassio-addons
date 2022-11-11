#!/command/with-contenv bashio
chown -R influxdb:influxdb /data
service influxdb start
