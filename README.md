# Kotiautomaatio

Tämä projekti sisältää docker-compose palvelut joilla Raspberry PI 3 tietokoneesta tehdään
Zigbee / Bluetooth hubi joka mahdollistaa kodin automatisoinnin.

Tällä hetkellä hubissa on seuraavat palvelut:

* bt-mqtt-gateway: Lukee RuuviTag sensorien mittausarvot käyttäen Bluetooth Low Energyä ja välittää MQTT:lle.
* Grafana: Näyttää InfluxDB kannassa olevat RuuviTagien mittausarvot graaffisina kuvaajina.
* InfluxDB: Tietokanta joka sisältää RuuviTagien mittausarvot.
* Mosquitto: Välittää MQTT viestejä bt-mqtt-gateway, zigbee2mqtt, Node-RED ja Telegraf palveluiden välillä.
* Node-RED: Varsinainen kotiautomaation aivot, kytkee eri sensorit ja painikkeet toisiinsa MQTT:n yli.
* Telegraf: Kerää MQTT viestejä (RuuviTagien mittausarvot) ja tallentaa ne InfluxDB tietokantaan.
* zigbee2mqtt: Välittää Zigbee protokollaa käyttävien etäohjattavien laitteiden viestejä MQTT:n.

Projekti perustuu paljolti seuraaviin lähteisiin:

* Mikrobitin artikkeleihin kotiautomaatiosta:
  * https://www.mikrobitti.fi/neuvot/opas-tee-se-itse-alykoti-nain-teet-kotiautomaatiota-juotoskolvilla/5d232e07-06d3-49a3-9164-2357411fe400
  * https://www.mikrobitti.fi/neuvot/opas-tee-se-itse-alykoti-osa-2-monipuolistetaan-kotijarjestelmaa-koodataan-ja-rakennetaan-lisaa/bc272811-7e1f-43fb-b5fe-aa56c1d640b3
* Kirjaan [Control You Home with Raspberry Pi - Koen Vervloesem](https://www.elektor.com/control-your-home-with-raspberry-pi)
* Demo projektiin: https://github.com/koenvervloesem/ruuvitag-demo

## Tarvittavat Laitteet

* Raspberry PI Model B 3+
* Wireless Zigbee CC2531 (laitteeseen flässättynä Z-Stack-firmware)
* Xiaomi Smart Wireless Switch (zigbee)
* Trådfri Pistorasia (zigbee)
* Trådfri lamppu x3 (zigbee)
* Trådfri painike/himmennin (zigbee)
* RuuviTag sensorit x2 (bluetooth)

## Asennus

### Kloonaa tämä repo:
```bash
cd ~
git clone https://github.com/jhakonen/koti-automaatio.git
cd koti-automaatio
```

### Luo TLS serifikaatit
Lataa mkcert -ohjelma:
```bash
wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.1/mkcert-v1.4.1-linux-arm
chmod +x mkcert
```
Luo TLS CA sertifikaatti:
```bash
./mkcert -install
cp ~/.local/share/mkcert/rootCA.pem certificates
```

Luo TLS sertifikaatti:
```bash
./mkcert kota.koti kota
cp kota.koti+1-key.pem certificates/key.pem
cp kota.koti+1.pem certificates/cert.pem
```

### Luo asetustiedostot palveluille:
```bash
cp bt-mqtt-gateway/config.sample.yaml bt-mqtt-gateway/config.yaml
cp telegraf/telegraf.sample.conf telegraf/telegraf.conf
cp zigbee2mqtt/configuration.sample.yaml zigbee2mqtt/configuration.yaml
```

### Aseta Grafanan oikeudet:
```bash
sudo chown -R 472:root grafana
```

### Käynnistä ympäristö:
```bash
docker-compose up -d
```

### Luo salasana MQTT palvelulle:
```bash
docker exec -ti mosquitto /usr/bin/mosquitto_passwd -c /mosquitto/config/passwords koti
```
Lisää antamasi salasana myös seuraaviin tiedostoihin:
* bt-mqtt-gateway/config.yaml
* telegraf/telegraf.conf
* zigbee2mqtt/configuration.yaml

Lopuksi käynnistä palvelut uudelleen:
```bash
docker-compose restart
```
