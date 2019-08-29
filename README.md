# Rasberry Pi x720 Hat Tools #
 
 * Battery monitor: view or send to Domoticz or MQTT
 * Safe shutdown workaround
 * Setting up the real time clock
 
```
git clone https://github.com/Tristan79/x720.git
```


#### Review of x720 ####

I fill in my rant here later!

http://www.raspberrypiwiki.com/index.php/X720

##### Cons #####

 * Jumper for auto shutdown is 3v DC (according to their specs). But battery meter is so bad it will power off (not safe shutdown) at values lower then ~3.15v high, which is much higher then 3v. Making the jumper useless. DO NOT SET JUMPER
 * If the shutdown problem occurs when removing the power plug, you have to remove the batteries!!! (geekworm you lying bastards!!!)
 * Network card can dissapear from your system completely, needing a power unplug (tested only without inserted batteries)
 * Little usb cable is reaaaly flimsy.
 * No wall mount holes in case
 * Battery meter is shit... I mean really shit...
 * Button on gpio triggered when unplugging the power, means spikes on (all/gpio?) electronics when switching from wired power to battery (and back)?
 * Undervoltage detected when pulling the power plug
 * Button for reboot or safe shutdown does not work without batteries present
 * Makes high pitch sound with no batteries
 * Sometimes make strange noise when pulling the power plug
 * Software provided is bad...  really really bad...
 * Support from either geekworm or suptronics.com is total crap (removing my comments on your youtube videos... really... and lying to your customers to sell, sell, sell...)
 * Very, very crappy hat...
 * Had to implement my own software
 
##### Pros #####

 * If it works it works for more then 8 hours on batteries... (but so does a powerbank) and you can use the battery monitor workaround to save shutdown
 * Can use network bonding to double network card (doubles the speed with speedtest-cli on a pi 3b)

##### Conclusion #####

Do not buy unless you known what you are doing and have considered the pro and cons (and work arounds)


#### Make e-vironment great again! ####

Make sure i2c is enabled with raspi-config.

Download the packages needed for running:
```
sudo apt-get install python3-pip i2c-tools
sudo pip3 install smbus
sudo pip3 install paho-mqtt
```

#### Tick, Tack ####

Setup the real time clock:

sudo nano /boot/config.txt

```
dtoverlay=i2c-rtc,ds1307
```

Remove fake hardware clock and disable one of the time synchronizers
```
sudo systemctl disable fake-hwclock
```

In /lib/udev/hwclock-set put # in front of these lines and the 2 lines containing --systz

```
if [-e /run/systemd/system ]; then
exit
fi
```

Reboot and test with

```
sudo hwclock -d
timedatectl status
```


Original code (do not use)
```
sudo sed -i '$ i rtc-ds1307' /etc/modules
sudo sed -i '$ i echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device' /etc/rc.local
sudo sed -i '$ i hwclock -s' /etc/rc.local
```

#### The not so good stuff ####
Set up the top button & stuff (do not use):
```
#sudo ./x720/x720button.sh
```

#### For Now Crappy Battery Monitor ####
Run the battery monitor 

```
./x720battery.py
```

or 

```
/home/pi/x720/x720battery.py
```

Make the battery monitor run (every minute) by editing crontab with the command:
```
sudo crontab -e
```
Add the following line:
```
* * * * * /home/pi/x720/x720battery.py
```

Create battery monitor configuration file x720battery.conf. Use the included example configuration file as base.

##### Save shutdown #####
Since the jumper for save shutdown and the original software provided is total $#!T, workaround. Use the voltage readout to safely shutdown and calculate the battery percentage. 

##### Domoticz #####
If you use domoticz: Create a Voltage, Text and two Percentage devices with the domoticzs dummy hardware. Look up their idx's and edit the x720battery.conf file. And make sure you enable it.

##### MQTT #####
If you use MQTT:
edit the x720battery.conf file. And make sure you enable it.
