#!/usr/bin/env python3
import struct
import smbus
import sys
import time
import configparser
import os

# Read config
config = configparser.ConfigParser()
os.chdir(os.path.dirname(sys.argv[0]))
try:
    config.read(r'x720battery.conf')
    x720_max = float(config.get('x720', 'max'))
    x720_min = float(config.get('x720', 'min'))
    
    domoticz_host = config.get('Domoticz', 'host')
    domoticz_port = config.get('Domoticz', 'port')
    domoticz_username = config.get('Domoticz', 'username')
    domoticz_password = config.get('Domoticz', 'password')
    domoticz_enabled = config.getboolean('Domoticz', 'enabled')
    idx_raw_capacity = config.get('Domoticz', 'rawcapacity')
    idx_capacity = config.get('Domoticz', 'capacity')
    idx_voltage  = config.get('Domoticz', 'voltage')
    idx_status   = config.get('Domoticz', 'status')
    
    mqtt_host = config.get('MQTT', 'host')
    mqtt_port = config.get('MQTT', 'port')
    mqtt_username = config.get('MQTT', 'username')
    mqtt_password = config.get('MQTT', 'password')
    mqtt_enabled = config.getboolean('MQTT', 'enabled')
    mqtt_topic = config.get('MQTT', 'topic')
except:
    print('Config file not found or error reading parameters')
    domoticz_enabled = False
    mqtt_enabled = False
    x720_min = 3.15
    x720_max = 4.1

x720_range = x720_max - x720_min

# Read Values
bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

def readVersion(bus):
    address = 0x36
    read = bus.read_word_data(address, 8)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    return swapped

def readVoltage(bus):
    address = 0x36
    read = bus.read_word_data(address, 2)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    voltage = ((swapped/16) * 1.25) / 1000
    return voltage

def readCapacity(bus):
    address = 0x36
    read = bus.read_word_data(address, 4)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped/256
    return capacity

raw_capacity = readCapacity(bus)
voltage = readVoltage(bus)
version = readVersion(bus)

status = "Normal"
"""
    if capacity < 5:
    status = "Low"
    elif capacity >= 100:
    status = "Max"
    elif capacity >= 95:
    status = "High"
    """

capacity = 0
if voltage >= x720_max:
    capacity = 100
    status = "Full"
elif voltage < x720_min:
    capacity = 0
    status = "Halt"
else:
    capacity = (voltage - x720_min) / (x720_range / 100)
    if capacity < 20:
        status = "Low"
    elif capacity > 80:
        status = "High"

# Print Status
s = status
if len(s) == 3:
    s = ' ' + s
s = ' ' + s

print ("Maxim MAX17043 v" + str(version))
print ("Voltage     : %5.2fV" % voltage)
print ("Raw Capacity: %5i%%" % raw_capacity)
print ("Battery     : %5i%%" % capacity)
print ("Status      : " + s)

# Handle Domoticz
if domoticz_enabled:
    import urllib.request
    import base64
    
    def domoticz(v,c,r,s):
        s = urllib.parse.quote(s)
        base64string = base64.encodebytes(('%s:%s' % (domoticz_username, domoticz_password)).encode()).decode().replace('\n', '')
        
        def domoticzrequest (url):
            url = "http://" + domoticz_host + ":" + str(domoticz_port) + "/json.htm?" + url
            request_ = urllib.request.Request(url)
            request_.add_header("Authorization", "Basic %s" % base64string)
            response = urllib.request.urlopen(request_)
            return response.read()
        
        domoticzrequest("type=command&param=udevice&idx="+ idx_voltage + "&nvalue=&svalue=" + str(v))
        domoticzrequest("type=command&param=udevice&idx="+ idx_capacity + "&nvalue=&svalue=" + str(c))
        domoticzrequest("type=command&param=udevice&idx="+ idx_raw_capacity + "&nvalue=&svalue=" + str(r))
        domoticzrequest("type=command&param=udevice&idx="+ idx_status + "&nvalue=0&svalue=" + s)
        print ('Domoticz Done')
    
    domoticz(voltage,capacity,raw_capacity,status)

# Handle MQTT
if mqtt_enabled:
    import paho.mqtt.client as mqtt
    client = mqtt.Client()
    client.username_pw_set(mqtt_username,mqtt_password)
    client.connect(mqtt_host,int(mqtt_port))
    client.publish(mqtt_topic + "/rawcapacity",raw_capacity)
    client.publish(mqtt_topic + "/capacity",capacity)
    client.publish(mqtt_topic + "/voltage",voltage)
    client.publish(mqtt_topic + "/status",status)
    # we need this delay!!!!
    time.sleep(0.05)
    client.disconnect()
    print ('MQTT Done')

