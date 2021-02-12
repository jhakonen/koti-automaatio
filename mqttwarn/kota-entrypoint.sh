#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Korvaa ympäristömuuttujat config tiedostoon
cat mqttwarn.ini | /env-korvaa.py > /tmp/mqttwarn.ini

# Kutsu kontin alkuperäistä entrypointia
MQTTWARNINI=/tmp/mqttwarn.ini mqttwarn
