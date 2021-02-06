#!/bin/bash
export BORG_PASSPHRASE="$1"

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/.."

borgmatic -c borgmatic -v 2
