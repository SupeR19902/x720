# x720
 x720 Tools

Make sure i2c is enabled with raspi-config.

Download the packages needed for running:
```
sudo ./x720/x720packages.sh
```

Setup the real time clock:
```
sudo ./x720/x720rtc.sh
```

Set up the top button (do not use):
```
#sudo ./x720/x720button.sh
```

Make the battery monitor run (every minute) by editing crontab with the command:
```
sudo crontab -e
```
Add the following line:
```
* * * * * /home/pi/x720/x720battery.py
```

Create battery monitor configuration file x720battery.conf. Use the example configuration file as base.

If you use domoticz: Create a Voltage, Text and Percentage devices with the domoticzs dummy hardware. Look up their idx's and edit the x720battery.conf file. And make sure you enable it.

If you use MQTT:
edit the x720battery.conf file. And make sure you enable it.
