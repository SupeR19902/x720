# x720
 x720 Tools

Download
------------------

Download packages

```
git clone https://github.com/Tristan79/x720.git
sudo apt-get install python3-pip
sudo pip3 install smbus
sudo pip3 install paho-mqtt
```

Install
------------------

Install real time clock and optional the x720 button

```
cd x720/
sudo ./x720rtc.sh
#sudo ./x720button.sh
```

Make the battery monitor run (every minute) by editing crontab with the command:

```
sudo crontab -e
```
Add the following line:

```
* * * * * /home/pi/x720/x720battery.py
```

Setup
------------------

Domoticz:

Create three custom sensors with domoticz dummy hardware.
Create a Voltage, Text and Percentage devices, look up their idx and edit the x720battery.conf file. Use the example file as base.

MQTT:

