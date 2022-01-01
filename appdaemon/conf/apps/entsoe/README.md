# Pörssihinnat ENTSO-E -palvelusta

Tämä AppDaemon applikaatio noutaa nykyisen ja tulevan päivän spot-hinnat tunnin
tarkkuudella.

## Käyttöönotto

1. Tallenna tämän kansion tiedostot AppDaemonin `/conf/apps/entsoe` -kansioon.

2. Lisää `/conf/apps/apps.yaml` -tiedostoon konfiguraatio:

```yaml
entsoe:
  module: entsoe
  class: Entsoe
  domain: <domaini>
  token: <api avain>
```

Mahdolliset domainit on listattu täällä:
  https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_areas

Esimerkiksi Suomen tapauksessa domaini on: 10YFI-1--------U

API avaimen saa seuraamalla ohjeita täältä:
  https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_authentication_and_authorisation

3. Käynnistä AppDaemon

## Tiedostojen muokkaus

Muutokset python tiedostoon AppDaemon tunnistaa automaattisesti ja se lataa
applikaation uudelleen joka kerta kun tiedostoa muokataan.

Seuraa AppDaemonin lokia jotta näet mahdolliset python virheet_

```bash
docker-compose logs -f appdaemon
```

Muutokset applikaation riippuvuuksiin tiedostossa `requirements.txt` vaatii
AppDaemonin uudelleenkäynnistyksen. Varmista että riippuvuus asentuu
onnistuneesti seuraamalla pavelun lokia:

```bash
docker-compose restart appdaemon && docker-compose logs -f --tail=50 appdaemon
```
