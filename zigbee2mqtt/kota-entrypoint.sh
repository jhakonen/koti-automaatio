#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Konfiguroi MQTT salasana
export ZIGBEE2MQTT_CONFIG_MQTT_PASSWORD="$MQTT_PASSWORD"

# Kutsu kontin alkuperäistä entrypointia
docker-entrypoint.sh npm start
