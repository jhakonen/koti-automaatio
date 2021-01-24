#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Konfiguroi MQTT salasana
export Z2MA_SETTINGS__MQTTPASSWORD="$MQTT_PASSWORD"

# Kutsu kontin alkuperäistä entrypointia
dotnet Zigbee2MqttAssistant.dll
