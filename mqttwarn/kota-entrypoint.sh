#!/bin/sh

# Korvaa docker salaisuudet config tiedostoon
cat mqttwarn.template.ini | /lisaa-salaisuudet.py > /tmp/mqttwarn.ini

# Kutsu kontin alkuperäistä entrypointia
MQTTWARNINI=/tmp/mqttwarn.ini mqttwarn
