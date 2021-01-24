#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Korvaa ympäristömuuttujat config.yaml tiedostoon
eval "echo \"$(cat /config.yaml.in)\"" > /config.yaml

# Kutsu kontin alkuperäistä entrypointia
/bin/sh -c /start.sh
