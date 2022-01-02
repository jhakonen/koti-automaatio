#!/usr/bin/env python3

# Tämä skripti lukee tekstiä stdin:stä, korvaa siinä olevat muuttujien nimet
# (muodossa $NIMI) salaisuuksilla /run/secrets hakemistosta ja tulostaa
# stdout:iin muokatun tekstin.

import string, sys, pathlib

def hae_salaisuudet():
	salaisuudet = {}
	hakemisto_polku = pathlib.Path('/run/secrets')
	for tiedosto_polku in hakemisto_polku.iterdir():
		with tiedosto_polku.open() as tiedosto:
			salaisuudet[tiedosto_polku.name] = tiedosto.read()
	return salaisuudet

sys.stdout.write(string.Template(sys.stdin.read()).safe_substitute(hae_salaisuudet()))
