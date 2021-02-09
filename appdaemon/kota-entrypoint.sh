#!/bin/sh

# Lataa docker salaisuudet /tmp/secrets.yaml tiedostoon
echo -n "" > /tmp/secrets.yaml
for filename in /run/secrets/*; do
  echo "$(basename $filename): $(cat $filename)" >> /tmp/secrets.yaml
done

# Kutsu kontin alkuperäistä entrypointia
./dockerStart.sh
