# Rasberry Pi suptronics/geekworm x720 Hat Tools #
 
 * Battery monitor: view status and/or send it to Domoticz or MQTT
 * Safe shutdown workaround in software
 * Setting up the real time clock
 
```
git clone https://github.com/Tristan79/x720.git
```

### ToDo ###
 * Top button press without rebooting (or at least use the button for something else) 
 * Shutting down the hat when shutdown (gpio 18 add it to /etc/rc0? as the final and last command)
 * Other power mangement GPIO stuff
 * Rant! (upvote in issues for youtube rant :-)
 * WOL...

### Review of x720 ###

I fill in my rant here later!

Only buy this if you are going to use the workarounds. And have almost no power outages. Pulling the plug CAN DAMAGE YOUR HAT AND YOUR PI!!! DO NOT PULL THE ADAPTER, AT LEAST WITH TESTING PULL THE PLUG AT THE PI END!!!

http://www.raspberrypiwiki.com/index.php/X720

#### Cons ####

##### HAT #####
* Mayor power spikes on gpio pins
* Undervoltage detected when pulling the power plug
* If the shutdown problem occurs when removing the power plug, your board is toast/fried/kaput!!!! (geekworm you lying bastards!!! see https://www.youtube.com/watch?v=enWHudsFcuw)... In my case, with fully charged batteries and no power plug inserted it will NOT TURN ON when pressing the top button (yeah.. it fried something). 
* The button script will cause reboots when power is lost
* Jumper for auto shutdown is 3v DC (according to their specs). But battery meter is so bad it will power off (not safe shutdown) at values lower then ~3.15v high, which is much higher then 3v. Making the jumper useless. DO NOT SET JUMPER
 * Network card can dissapear from your system completely, needing a power unplug and removal of the batteries
 * Little usb cable is reaaaly flimsy and does sometimes not work (not related to network card disappearing thou)
 * Battery meter is shit... I mean really shit...
 * Button on gpio triggered when unplugging the power, means spikes on (all/gpio?) electronics when switching from wired power to battery (and back)?
 * Button for reboot or safe shutdown does not work without batteries present (their specs say otherwise)
 * Makes high pitch sound with no batteries (alas poor dogs & cats... and think of your little children which have still good ears)
 * Sometimes make strange noise when pulling the power plug
 * Software provided is bad...  really really bad...
 * Support from either geekworm or suptronics.com is total crap (geekworm... removing my comments on your youtube videos... really... and lying to your customers to sell, sell, sell...)
 * Very, very crappy hat... damages really fast with power outages
 * Had to implement my own software
 
##### Case #####
 * No wall mount holes in case
 * Case Pi microusb has a big X with a circle... instead of closing it up
 * Case seales up the 5v output from the hat
 * Case becomes static...
  
#### Pros ####

 * If it works it works for more then 8 hours on batteries... (but so does a powerbank) but you can use the battery monitor workaround to save shutdown making it somewhat an ups... almost.
 * Can use network bonding to double network card (doubles the speed with speedtest-cli on a pi 3b)
 * Like the case (when I am not touching it see last con)

##### Conclusion #####

Do not buy unless you known what you are doing and have considered the pro and cons (and work arounds). I already fried one board...

### So what... Tested on... ###
Buster,...

#### Make e-vironment great again! ####

Make sure i2c is enabled with raspi-config.

Download the packages needed for running:
```
sudo apt-get install python3-pip i2c-tools
sudo pip3 install smbus
sudo pip3 install paho-mqtt
```

### Tick, Tack ###

Setup the real time clock:

sudo nano /boot/config.txt

```
dtoverlay=i2c-rtc,ds1307
```

Remove fake hardware clock
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

### Software Battery Monitor ###
Run the battery monitor 

```
./x720battery.py
```

or 

```
/home/pi/x720/x720battery.py
```

Make the battery monitor and auto shutdown feature run (every minute) by editing crontab with the command:

```
sudo nano /etc/crontab
```

Add the line

```
* * * * * root /home/pi/x720/x720battery.py
```

Create battery monitor configuration file x720battery.conf. Use the included example configuration file as base.

##### Save shutdown #####
Since the jumper for save shutdown and the original software provided is total $#!T, workaround. Use the voltage readout to safely shutdown and calculate the battery percentage. You can adjust the values in the configuration file. And you can monitor the values with MQTT or Domoticz. Your values may different depending on your batteries.

##### Domoticz #####
If you use domoticz: Create a Voltage, Text and two Percentage devices with the domoticzs dummy hardware. Look up their idx's and edit the x720battery.conf file. And make sure you enable it.

##### MQTT #####
If you use MQTT:
edit the x720battery.conf file. And make sure you enable it.

## Very Optional Features ##

This can also be used with other network cards and other debian installations. No x720 or Pi needed. But because I figured this out with a Pi and with a x720 (total cost: 3 weeks, yeah...), lets share... I probably need to add some more info...
So fast track to bonding...

### Bonding ###

Reference: https://raspberrypi.stackexchange.com/revisions/78788/15

Using two wires as one!

This will be a very short walkthrough of bonding... if you have issues or missing info well post an issue.

I currently use a netgear gs116 which support LAG, which actually is XOR bonding (thanks netgear :( for letting me think I have all the functionallity of LACP but I only got the subset for XOR bonding... netgear just as cheap as their chinese counterparts, only they can hide it better... vommit... documentation just as shit... what is it with you hardware sellers. Make a good product instead of manipulating your customers, you do not have to be manipulating, lying, cheating and be greedy to make money) If you use LACP or XOR bonding do not forget to configure your switch.

You can use FULL LACP or Active Backup... (google is your friend) for the parameters needed.

I switches over to systemd networking instead of /etc/network/interfaces on the Pi. I tried the default option with the /etc/network/interfaces and it will result in connecting to wifi (if configured and available) instead of the bond in 1 out of 10 situations..., Which is behaviour you do not want... Finally found a solution... Systemd networking fix it. Systemd has very very very poor documentation... :-( Like why if I use static and dhcp mixed with systemd the metric (order of network cards) is fucked? And I have to manually set the metric myself... which is a pain in the butt... Anyway all things have good and bad side, not?

Anyway bonding 180mb throughput instead of 90mbit (maybe more on the newer models)

```
sudo nano /etc/resolvconf.conf
```

Add

```
# Set to NO to disable resolvconf from running any subscribers. Defaults to YES.
resolvconf=NO
```

Run to switch over to systemd networking

```
sudo systemctl mask networking.service
sudo systemctl mask dhcpcd.service
sudo mv /etc/network/interfaces /etc/network/interfaces~
sudo systemctl enable systemd-networkd.service
sudo systemctl enable systemd-resolved.service
# for fast prompt on screen when connecting with HDMI
sudo systemctl disable systemd-networkd-wait-online.service
sudo systemctl mask systemd-networkd-wait-online.service
sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
```

##### Optional Wifi #####

```
sudo nano /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=DE

network={
    ssid="CHANGE"
    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP TKIP
    group=CCMP TKIP
    psk="CHANGE"
}
```

Run it...

```
sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
sudo systemctl disable wpa_supplicant.service
sudo systemctl enable wpa_supplicant@wlan0.service
```

Configure it...
```
sudo nano /etc/systemd/network/08-wifi.network
```

```
[Match]
Name=wl*

[Network]
# to use static IP (with your settings) toggle commenting the next 5 lines.
#Address=192.168.1.87/24
#Gateway=192.168.1.1
DHCP=yes

[DHCP]
RouteMetric=20
```

##### Ethernet #####
The commented out lines are for Active Backup...

```
sudo nano /etc/systemd/network/12-bond0.netdev
```

```
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=balance-xor  
#Mode=active-backup
#PrimaryReselectPolicy=always
TransmitHashPolicy=layer3+4
MIIMonitorSec=1s
```

```
sudo nano /etc/systemd/network/16-bond0-add-eth.network
```

Split these in two files for ActiveBackup, one with PrimarySlave and the other not... (Name=eth0 and eth1 instead of e*)

```
[Match]
Name=e*
[Network]
Bond=bond0
#PrimarySlave=true
```

Very optional!!! If you use ActiveBackup you can add your Wifi if you want to... (failover to wifi if lan cables are pulled)

sudo nano /etc/systemd/network/20-bond0-add-wifi.network

```
[Match]
Name=wl*
[Network]
Bond=bond0
```

I do not use Wifi... and you can not do a bond in bond as on some other OSes :( so...

To continue...

```
sudo nano /etc/systemd/network/24-bond0-up.network
```

```
[Match]
Name=bond0
[Network]
DHCP=yes
#VLAN=bond0.1003

[DHCP]
RouteMetric=10
```

#### VLAN ####

This is very, very, mucho very optional.... If you want a vlan over a bond...

```
sudo nano /etc/systemd/network/25-bond0-vlan1003.netdev
```

```
[NetDev]
Name=bond0.1003
Kind=vlan

[VLAN]
Id=1003
```

Sidenote: The vlan 1003 is the guest network of the Apple Airports I have, which I use as a second (wifi) network running my IOT devices... In my case vlan 1003 had no internet access. Make sure the Airport is in bridge mode... NOT in any other mode...

You can use dhcp from another device on the vlan, but I use the build in DHCP server

```
sudo nano /etc/systemd/network/26-bond0-vlan1003.network
```

```
[Match]
Name=bond0.1003

[Network]
Address=10.0.1.1
DHCPServer=yes
#IPMasquerade=yes

[DHCPServer]
PoolOffset=100
PoolSize=100
EmitDNS=yes
DNS=10.0.0.2
```

If you set IPMasquerade=yes, it will bridge your networks.

##### Optional Clean Up #####
```
sudo apt install deborphan
sudo apt --autoremove purge openresolv -y
sudo apt --autoremove purge ifupdown -y
sudo apt --autoremove purge dhcpcd5 -y
sudo apt --autoremove purge isc-dhcp-client isc-dhcp-common -y
sudo apt --autoremove purge $(deborphan)
sudo apt --autoremove purge $(deborphan) #two times
```

##### Extra usefull command #####

```
cat /proc/net/bonding/bond0 
```

```
sudo apt-get install arp-scan
sudo arp-scan --interface=bond0.1003 --localnet 
sudo apt-get install nmap
sudo nmap -sP 10.0.1.0/24 
sudo netstat -plunt
pip3 install speedtest-cli
speedtest
```

Please try the speedtest (-single parameter) to see throughput is doubled (unless your isp is too slow)

##### Do not bridge mdns #####
```
sudo nano avahi-daemon.conf 
```

```
deny-interfaces=bond0.1003
allow-interfaces=bond0
```
