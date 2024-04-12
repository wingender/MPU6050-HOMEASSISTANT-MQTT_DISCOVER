import time
import json
from mqtt_config import mqtt_client, connect
import mpu6050

# MQTT and Home Assistant configuration
DISCOVERY_PREFIX = "homeassistant"
COMPONENT = "number"
OBJECT_ID = "mpu6050"
DEVICE_NAME = "MPU6050 Sensor"
MANUFACTURER = "Generic"
MODEL = "MPU6050 Model"

def publish_discovery():
    """Publishes sensor configuration to Home Assistant via MQTT for automatic discovery."""
    sensor_types = ['gyro_x', 'gyro_y', 'gyro_z', 'accel_x', 'accel_y', 'accel_z']
    units = {'gyro_x': '°/s', 'gyro_y': '°/s', 'gyro_z': '°/s', 'accel_x': 'm/s²', 'accel_y': 'm/s²', 'accel_z': 'm/s²'}
    for sensor in sensor_types:
        config_topic = f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/{sensor}/config"
        payload = {
            "name": f"{DEVICE_NAME} {sensor.replace('_', ' ').title()}",
            "state_topic": f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/{sensor}/state",
            "command_topic": f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/{sensor}/set",
            "unit_of_measurement": units[sensor],
            "unique_id": f"{OBJECT_ID}_{sensor}",
            "availability_topic": f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": [f"{OBJECT_ID}_identifier"],
                "name": DEVICE_NAME,
                "model": MODEL,
                "manufacturer": MANUFACTURER
            }
        }
        mqtt_client.publish(config_topic, json.dumps(payload), qos=1, retain=True)

def update_sensors():
    """Continuously read, scale, and publish sensor data."""
    mpu6050.MPU_Init()
    accel_offsets, gyro_offsets = mpu6050.calibrate_sensors()
    while True:
        ax, ay, az = [mpu6050.read_raw_data(getattr(mpu6050, f'ACCEL_{axis}OUT_H')) - accel_offsets[i] for i, axis in enumerate('XYZ')]
        gx, gy, gz = [mpu6050.read_raw_data(getattr(mpu6050, f'GYRO_{axis}OUT_H')) - gyro_offsets[i] for i, axis in enumerate('XYZ')]
        
        # Scaling factors for gyro and accel
        ax, ay, az = [a / 16384.0 * 9.81 for a in (ax, ay, az)]  # Accel scaling to m/s²
        gx, gy, gz = [g / 131.0 for g in (gx, gy, gz)]  # Gyro scaling to °/s

        data = {
            'gyro_x': gx, 'gyro_y': gy, 'gyro_z': gz,
            'accel_x': ax, 'accel_y': ay, 'accel_z': az
        }
        
        for sensor, value in data.items():
            state_topic = f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/{sensor}/state"
            availability_topic = f"{DISCOVERY_PREFIX}/{COMPONENT}/{OBJECT_ID}/{sensor}/availability"
            mqtt_client.publish(availability_topic, "online", qos=1, retain=True)
            mqtt_client.publish(state_topic, float(value), qos=1, retain=True)
        time.sleep(1)

if __name__ == "__main__":
    connect()
    publish_discovery()
    update_sensors()
