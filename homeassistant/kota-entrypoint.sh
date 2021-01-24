#!/bin/sh

# Lataa docker salaisuudet ympäristömuuttujiin
for filename in /run/secrets/*; do
  export $(basename $filename)=$(cat $filename)
done

# Kutsu kontin alkuperäistä entrypointia
/init
