Upgrade from influxdb 1.8 na influxdb 2

1. Vyzálohovat influxdb verze 
2. Nainstalovat influxdb2
3. Pak teprve poprvé spustíme doplňek.
4. Pak spustíme Portainer a připojíme i influxu
5. Spustím příkazy
dpkg -P influxdb2
rm /etc/influxdb/config.toml
rm -r /data/influxdb
dpkg --install /tmp/influxdb.deb
rm /etc/influxdb/config.toml
rm -r /root/.influxdbv2
apt update
apt install sudo


6. Nakopírovat data z Influxu 1: cp -r addons/data/a0d7b954_influxdb/influxdb addons/data/99d9d1d4_influxdb2   #zvolíme správné adresáře
7. Spustíme upgrade
/etc/influxdb2-upgrade.sh

7. Stopnout influxd a vygenerovat nový operator token
kill -9 270
influxd recovery auth create-operator --bolt-path /data/influxdb/influxd.bolt --username admin --org Home

8. Pak mohu například vytvářet uživatele influx user create -n onemeter -p Onemeter,3390 -o home -t {token}
