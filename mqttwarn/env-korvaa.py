#!/usr/bin/env python3

# Tämä skripti lukee tekstiä stdin:stä, korvaa siinä olevat muuttujien nimet
# (muodossa $NIMI) ympäristömuuttujilla ja tulostaa stdout:iin muokatun tekstin.
#
# Esim:
#   echo '-->$FOO<--' | FOO=BAR ./env-korvaa.py
# Tulostaa:
#   -->BAR<--

import os, string, sys
sys.stdout.write(string.Template(sys.stdin.read()).safe_substitute(os.environ))
