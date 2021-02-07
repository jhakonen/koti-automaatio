#!/bin/bash
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

cd "$SCRIPT_DIR/.."

export BORG_PASSPHRASE="$(cat secrets/BORG_PASSPHRASE)"
borgmatic -c borgmatic -v 2
