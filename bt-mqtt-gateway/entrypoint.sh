#!/bin/sh

INPUT_CONFIG_FILE=$1
OUTPUT_CONFIG_FILE=$2

# Korvaa ympäristömuuttujat config.yaml tiedostoon
eval "echo \"$(cat "$INPUT_CONFIG_FILE")\"" > "$OUTPUT_CONFIG_FILE"

# Kutsu kontin alkuperäistä entrypointia
/bin/sh -c /start.sh
