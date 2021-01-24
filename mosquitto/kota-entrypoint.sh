#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Konfiguroi MQTT salasana
/usr/bin/mosquitto_passwd -b /mosquitto/config/passwords koti "$MQTT_PASSWORD"

# Kutsu kontin alkuperäistä entrypointia
/docker-entrypoint.sh /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf

