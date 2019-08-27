#!/usr/bin/env python3
import struct
import smbus
import sys
import time
import configparser

# Read config
config = configparser.ConfigParser()
config.read(r'x720battery.conf')
domoticz_host = config.get('Domoticz', 'host')
domoticz_port = config.get('Domoticz', 'port')
domoticz_username = config.get('Domoticz', 'username')
domoticz_password = config.get('Domoticz', 'password')
domoticz_enabled = config.getboolean('Domoticz', 'enabled')
idx_capacity = config.get('Domoticz', 'capacity')
idx_voltage  = config.get('Domoticz', 'voltage')
idx_status   = config.get('Domoticz', 'status')

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

capacity = readCapacity(bus)
voltage = readVoltage(bus)
version = readVersion(bus)
status = "Normal"
if capacity < 5:
    status = "Low"
elif capacity >= 100:
    status = "Max"
elif capacity >= 95:
    status = "High"

# Print Status
print ("Maxim MAX17043 v" + str(version))
print ("Voltage: %5.2fV" % voltage)
print ("Battery: %5i%%" % capacity)
print ("Status : " + status)

# Handle Domoticz
if domoticz_enabled:
    import urllib.request
    import base64

    def domoticz(v,c,s):
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
            domoticzrequest("type=command&param=udevice&idx="+ idx_status + "&nvalue=0&svalue=" + s)
            print ('Domoticz Done')

    domoticz(voltage,capacity,status)
