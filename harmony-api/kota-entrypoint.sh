#!/bin/sh

node /config.js > /tmp/config.json
export CONFIG_DIR=/tmp

# Kutsu kontin alkuperäistä entrypointia
npm start
