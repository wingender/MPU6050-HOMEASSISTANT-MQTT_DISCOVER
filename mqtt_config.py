# File: mqtt_config.py

import paho.mqtt.client as mqtt
from uuid import uuid4

# MQTT Broker Settings
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = "password"
CLIENT_ID = f"mpu6050_{uuid4()}"

# Create an MQTT client instance
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)

# MQTT Event Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker, error code:", rc)

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")

def on_publish(client, userdata, mid):
    print("Published message with MID:", mid)

# Set MQTT event callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

def connect():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
