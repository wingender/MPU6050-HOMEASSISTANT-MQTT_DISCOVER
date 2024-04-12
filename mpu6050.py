import smbus
import time

# Constants for MPU6050 register addresses
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

bus = smbus.SMBus(1)  # Assumes the MPU6050 is connected to I2C bus 1
Device_Address = 0x68  # MPU6050 I2C address

def MPU_Init():
    """Initializes the MPU6050 to +/- 2g accelerometer and +/- 250 degrees/second gyroscope."""
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 0x80)  # Reset the device
    time.sleep(0.1)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 0x03)  # Clock source = Gyro-Z
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)     # Set sample rate = 1 kHz / (1 + 7) = 125 Hz
    bus.write_byte_data(Device_Address, ACCEL_CONFIG, 0)   # Set accelerometer to +/- 2g
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 0)    # Set gyroscope to +/- 250 degrees/sec
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)     # Enable data ready interrupt
    time.sleep(0.1)

def read_raw_data(addr):
    """Reads two bytes of data from the MPU6050 and converts it to a 16-bit signed value."""
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = ((high << 8) | low)
    if value > 32767:
        value -= 65536
    return value

def calibrate_sensors(samples=100):
    """Calibrates the MPU6050 sensors by calculating offsets."""
    ax_off = ay_off = az_off = gx_off = gy_off = gz_off = 0
    print("Calibrating MPU6050...")
    for i in range(samples):
        ax_off += read_raw_data(ACCEL_XOUT_H)
        ay_off += read_raw_data(ACCEL_YOUT_H)
        az_off += read_raw_data(ACCEL_ZOUT_H) - 16384  # Assuming 1g is on Z-axis
        gx_off += read_raw_data(GYRO_XOUT_H)
        gy_off += read_raw_data(GYRO_YOUT_H)
        gz_off += read_raw_data(GYRO_ZOUT_H)
        time.sleep(0.01)  # Sleep to allow other processes
    ax_off /= samples
    ay_off /= samples
    az_off /= samples
    gx_off /= samples
    gy_off /= samples
    gz_off /= samples
    return (ax_off, ay_off, az_off), (gx_off, gy_off, gz_off)
