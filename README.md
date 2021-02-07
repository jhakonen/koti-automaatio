# Kotiautomaatio

Tämä projekti sisältää docker-compose palvelut joilla Raspberry PI 3 tietokoneesta tehdään
Zigbee / Bluetooth hubi joka mahdollistaa kodin automatisoinnin.

Tällä hetkellä hubissa on seuraavat palvelut:

* bt-mqtt-gateway: Lukee RuuviTag sensorien mittausarvot käyttäen Bluetooth Low Energyä ja välittää MQTT:lle.
* Grafana: Näyttää InfluxDB kannassa olevat RuuviTagien mittausarvot graaffisina kuvaajina.
* Heimdall: Tarjoaa Dashboardin josta voi helposti käynnistää palveluiden webbi-käyttöliittymiä
* HomeAssistant: Kotiautomaation hallinta, kytkee eri sensorit ja painikkeet toisiinsa MQTT:n yli.
* InfluxDB: Tietokanta joka sisältää RuuviTagien mittausarvot.
* Mosquitto: Välittää MQTT viestejä bt-mqtt-gateway, zigbee2mqtt, Node-RED ja Telegraf palveluiden välillä.
* Node-RED: Kotiautomaation hallinta, kytkee eri sensorit ja painikkeet toisiinsa MQTT:n yli.
* Telegraf: Kerää MQTT viestejä (RuuviTagien mittausarvot) ja tallentaa ne InfluxDB tietokantaan.
* Zigbee2Mqtt: Välittää Zigbee protokollaa käyttävien etäohjattavien laitteiden viestejä MQTT:n.
* Zigbee2MqttAssistant: Webbikäyttöliittymä Zigbee2Mqtt:n ohjaamiseen.

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
openssl x509 -inform PEM -outform DER -in certificates/rootCA.pem -out rootCA.crt
```

Luo TLS sertifikaatti:
```bash
./mkcert kota.koti kota
cp kota.koti+1-key.pem certificates/key.pem
cp kota.koti+1-key.pem heimdall/keys/cert.key 
cp kota.koti+1.pem certificates/cert.pem
cp kota.koti+1.pem heimdall/keys/cert.crt
```

Lataa rootCA.pem ja rootCA.crt tietokoneille ja mobiililaitteille ja aseta CA sertifikaatti luotetuksi.
PEM-päätteisen saa yleensä asennettua Linux ympäristöön, CRT-päätteinen tiedosto käy Androidiin asennukseen. 

### Luo hakemistot
```bash
mkdir -p \
  grafana/etc/provisioning \
  grafana/lib \
  grafana/dashboards \
  mosquitto/config \
  mosquitto/data \
  mosquitto/log \
  influxdb/var \
  homeassistant/config

```

### Aseta MQTT salasana
```bash
echo "<salasana>" > secrets/MQTT_PASSWORD
```

### Käynnistä ympäristö:
```bash
docker-compose up -d
```

### Konfiguroi Heimdall
1. Avaa webbiselaimeen osoite https://kota.koti/
2. Aseta admin käyttäjän nimi ja salasana
3. Lisää ohjelma Node-RED:lle (Title: NodeRed, URL: http://kota.koti:1880/)
4. Lisää ohjelma Grafanalle (Title: Grafana, URL: http://kota.koti:3000/)
5. Lisää ohjelma Zigbee2MqttAssistantille (Title: Zigbee2MqttAssistant, App Type: None, URL: http://kota.koti:8880/, Logo: https://raw.githubusercontent.com/Koenkk/zigbee2mqtt/master/images/logo.png)
6. Lisää ohjelma HomeAssistantille (Title: HomeAssistant, URL: https://kota.koti:8123/)

## Varmuuskopiointi

Asenna Borg Backup ohjelmistot:
```bash
sudo apt install borg borgmatic
```

Kokeile että varmuuskopiointi toimii:
```bash
~/koti-automaatio/borgmatic/run-backup.sh <repo salasana>
```

Lisää varmuuskopiointi crontabiin:
```bash
crontab -e
```
```crontab
0 0 * * * ~/koti-automaatio/borgmatic/run-backup.sh <repo salasana>
```
