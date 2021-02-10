import json
import mqttapi as mqtt
import requests
import time

MQTT_MESSAGE = 'MQTT_MESSAGE'
MQTT_TOPIC_HA = 'harmony-api/hubs/#'

class HarmonyAPI(mqtt.Mqtt):

    def initialize(self):
        self.hubs = []
        self.previous_hubs = []
        self.hub_activities = {}
        self.previous_hub_activities = {}
        self.activity_commands = {}
        self.previous_activity_commands = {}
        self.last_retrieve = 0
        self.set_namespace("mqtt")
        self.listen_event(self.on_ha_message, MQTT_MESSAGE, wildcard=MQTT_TOPIC_HA)
        self.mqtt_subscribe(MQTT_TOPIC_HA)

    def terminate(self):
        for hub_slug in self.hubs:
            self.hub_activities[hub_slug].clear()
            self.update_activities_config(hub_slug)
        self.hubs.clear()
        self.update_hubs_config()
        self.mqtt_unsubscribe(MQTT_TOPIC_HA)

    def on_ha_message(self, event_name, data, kwargs):
        # self.log('message: %s', data['topic'])
        self.retrieve_hubs()

    def retrieve_hubs(self):
        if self.last_retrieve > (time.time() - 5):
            return
        self.last_retrieve = time.time()
        # self.log('retriving hubs')
        self.hubs = self.query_harmony_api('/hubs')['hubs']
        # self.log('hubs: %s', self.hubs)
        self.update_hubs_config()
        for hub_slug in self.hubs:
            activities = self.query_harmony_api(f'/hubs/{hub_slug}/activities')['activities']
            # self.log('hub %s activities: %s', hub_slug, [act['label'] for act in activities])
            self.hub_activities[hub_slug] = activities
            self.update_activities_config(hub_slug)

    def query_harmony_api(self, path):
        host = self.args['harmony_api_host']
        port = self.args['harmony_api_port']
        response = requests.get(f'http://{host}:{port}{path}')
        if response.status_code != 200:
            raise RuntimeError(f'Harmony API query {path} returned {response.status_code}')
        return response.json()

    def update_hubs_config(self):
        added = set(self.hubs) - set(self.previous_hubs)
        removed = set(self.previous_hubs) - set(self.hubs)
        for hub_slug in added:
            self.log('Adding hub: %s', hub_slug)
            self.mqtt_publish(
                f'homeassistant/sensor/{hub_slug}/current_activity/config',
                json.dumps({
                'name': f'{hub_slug} current activity',
                'unique_id': f'harmony-api/{hub_slug}/current_activity',
                'state_topic': f'harmony-api/hubs/{hub_slug}/current_activity',
                'device': self.build_device_config(hub_slug),
                }),
                retain=True
            )
        for hub_slug in removed:
            self.log('Removing hub: %s', hub_slug)
            self.mqtt_publish(
                f'homeassistant/sensor/{hub_slug}/current_activity/config',
                '',
                retain=True
            )
        self.previous_hubs = list(self.hubs)

    def build_device_config(self, hub_slug):
        return {
            'identifiers': f'harmony-api/{hub_slug}',
            'manufacturer': 'Logitech',
            'model': 'Harmony Hub',
            'name': hub_slug
        }

    def update_activities_config(self, hub_slug):
        activities = self.hub_activities[hub_slug]
        previous_activities = self.previous_hub_activities.get(hub_slug, [])
        act_slugs = [act['slug'] for act in activities]
        prev_act_slugs = [act['slug'] for act in previous_activities]
        added_slugs = set(act_slugs) - set(prev_act_slugs)
        removed_slugs = set(prev_act_slugs) - set(act_slugs)
        for act_slug in added_slugs:
            activity = next(act for act in activities if act['slug'] == act_slug)
            act_label = activity['label']
            self.log('Adding hub %s activity: %s', hub_slug, act_slug)
            payload = {
                'name': f'{hub_slug} activity: {act_label}',
                'unique_id': f'harmony-api/{hub_slug}/activities/{act_slug}',
                'state_topic': f'harmony-api/hubs/{hub_slug}/activities/{act_slug}/state',
                'command_topic': f'harmony-api/hubs/{hub_slug}/activities/{act_slug}/command',
                'payload_on': 'on',
                'payload_off': 'off',
                'device': self.build_device_config(hub_slug),
            }
            if act_slug == 'poweroff':
                payload['name'] = hub_slug
                payload['icon'] = 'hass:remote'
            self.mqtt_publish(
                f'homeassistant/switch/{hub_slug}-{act_slug}/state/config',
                json.dumps(payload),
                retain=True
            )
        for act_slug in removed_slugs:
            self.log('Removing hub %s activity: %s', hub_slug, act_slug)
            self.mqtt_publish(
                f'homeassistant/switch/{hub_slug}-{act_slug}/state/config',
                '',
                retain=True
            )
        self.previous_hub_activities[hub_slug] = list(self.hub_activities[hub_slug])
