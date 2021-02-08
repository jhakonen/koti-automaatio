const fs = require('fs');

const config = {
  hubs: [
    {
      ip: '192.168.1.229',
      name: 'Olohuone v2'
    }
  ],
  enableHTTPserver: true,
  mqtt_host: 'mqtt://mosquitto',
  topic_namespace: 'harmony-api',
  mqtt_options: {
    port: 1883,
    username: 'koti',
    password: fs.readFileSync('/run/secrets/MQTT_PASSWORD', 'utf8'),
    rejectUnauthorized: false,
    retain: true
  }
};

console.log(JSON.stringify(config, null, 2));
