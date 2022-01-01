import datetime
import json
import pprint
import xml.etree.ElementTree as ET

import dateutil
import mqttapi as mqtt
import requests

ENTSOE_URL = 'https://transparency.entsoe.eu/api'

MQTT_MESSAGE = 'MQTT_MESSAGE'
MQTT_TOPIC_PÖRSSIHINNAT_HAE = 'entsoe/pörssisähkö-hinnat/hae'
MQTT_TOPIC_PÖRSSIHINNAT_VASTAUS = 'entsoe/pörssisähkö-hinnat/vastaus'
MQTT_TOPIC_PÖRSSIHINNAT_VIRHE = 'entsoe/pörssisähkö-hinnat/virhe'

class Entsoe(mqtt.Mqtt):
  '''
  AppDaemon applikaatio joka noutaa nykyisen ja tulevan päivän spot-hinnat
  tunnin tarkkuudella.
  '''
  def initialize(self):
    '''
    Applikaation alustusmetodi. Tätä kutsutaan kun AppDaemon käynnistyy tai kun
    applikaatio ladataan uudelleen (esim. tätä tiedostoa muokatessa).
    '''
    self.set_namespace('mqtt')
    self.listen_event(self.hae_pörssihinnat, MQTT_MESSAGE, topic=MQTT_TOPIC_PÖRSSIHINNAT_HAE)
    self.mqtt_subscribe(MQTT_TOPIC_PÖRSSIHINNAT_HAE)

  def terminate(self):
    '''
    Applikaation purkumetodi. Tätä kutsutaan kun AppDaemon sammutetaan tai kun
    applikaatio ladataan uudelleen (esim. tätä tiedostoa muokatessa).
    '''
    self.mqtt_unsubscribe(MQTT_TOPIC_PÖRSSIHINNAT_HAE)

  def log(self, *args, **kwargs):
    '''
    Poistaa ASCII koodauksen lokiviesteistä ettei se sössi ääkkösiä, muuten
    sama kuin mqtt.Mqtt.log().
    '''
    super().log(*args, **dict(kwargs, ascii_encode=False))

  def hae_pörssihinnat(self, event_name, data, kwargs):
    '''
    Hakee pörssihinnat ENTSO-E palvelusta ja lähettää sieltä saadut tuntihinnat
    MQTT otsikkoon MQTT_TOPIC_PÖRSSIHINNAT_VASTAUS ja mahdolliset virheet
    otsikkoon MQTT_TOPIC_PÖRSSIHINNAT_VIRHE.

    Palvelun REST API:n kuvaus:
      https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_day_ahead_prices_12_1_d
    '''
    try:
      self.log('hae_pörssihinnat: %s', data)
      tänään = datetime.datetime.now(datetime.timezone.utc).replace(minute=0)
      huomenna = tänään + datetime.timedelta(days=1)
      vastaus = requests.get(ENTSOE_URL, params={
        'securityToken': self.args['token'],
        'documentType': 'A44',
        'in_Domain': self.args['domain'],
        'out_Domain': self.args['domain'],
        'timeInterval': '/'.join([
          self.iso_muotoon(tänään),
          self.iso_muotoon(huomenna),
        ])
      })
      vastaus.raise_for_status()
      # Debuggausta varten:
      # self.log('vastaus: %s', vastaus.text)
      tuntihinnat = self.kerää_tuntihinnat(vastaus.text)
      self.mqtt_publish(MQTT_TOPIC_PÖRSSIHINNAT_VASTAUS, json.dumps(tuntihinnat))
      self.log('hae_pörssihinnat vastaus: %d tuntihintaa', len(tuntihinnat))
    except Exception as error:
      self.mqtt_publish(MQTT_TOPIC_PÖRSSIHINNAT_VIRHE, self.poista_salaisuudet(str(error)))
      self.log('hae_pörssihinnat virhe: %s', error)
      raise

  def iso_muotoon(self, aika):
    '''
    Muuttaa datetime ajan ISO 8601 muotoon jonka ENTSO-E:n API hyväksyy,
    esim: '2021-12-31T18:18Z'. Sisään syötetty aika pitää olla UTC
    aikavyöhykkeellä.
    '''
    return aika.isoformat(timespec='minutes').replace('+00:00', 'Z')

  def kerää_tuntihinnat(self, xml_dokumentti):
    '''
    Kerää tuntihinnat annetusta xml dokumentista. esimerkki dokumentista löytyy
    API:n kuvauksesta (katso URL hae_pörssihinnat funktion apidocista).
    Palauttaa tuntihinnat muodossa:
      [
        { aika: "2021-12-31T00:00Z", hinta 12.30 },
        { aika: "2021-12-31T01:00Z", hinta 15.70 },
        ...
        { aika: "2021-12-31T23:00Z", hinta 16.45 }
      ]
    '''
    tuntihinnat = []
    ns = { 'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0' }
    xml_juuri = ET.fromstring(xml_dokumentti)
    for period_elementti in xml_juuri.findall('.//ns:Period', ns):
      alku = dateutil.parser.isoparse(
        period_elementti.findtext('./ns:timeInterval/ns:start', None, ns))
      for point_elementti in period_elementti.findall('./ns:Point', ns):
        tunti = point_elementti.findtext('./ns:position', None, ns)
        hinta = point_elementti.findtext('./ns:price.amount', None, ns)
        aika = alku + datetime.timedelta(hours=int(tunti)-1)
        tuntihinta = {
          'aika': self.iso_muotoon(aika),
          'hinta': float(hinta)
        }
        tuntihinnat.append(tuntihinta)
        # Debuggausta varten:
        # self.log('tuntihinta: %s', tuntihinta)
    return tuntihinnat

  def poista_salaisuudet(self, teksti):
    '''
    Poistaa annetusta merkkijonosta API security tokenin jotta se ei vuoda
    applikaation ulkopuolelle.
    '''
    return teksti.replace(self.args['token'], '<poistettu>')
