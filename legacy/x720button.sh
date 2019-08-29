#!/bin/bash
# do not use, unplugging the hat will result in a reboot or shutdown due to this script

SHUTDOWN=4
REBOOTPULSEMINIMUM=200
REBOOTPULSEMAXIMUM=600
echo "$SHUTDOWN" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio$SHUTDOWN/direction
BOOT=17
echo "$BOOT" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio$BOOT/direction
echo "1" > /sys/class/gpio/gpio$BOOT/value

echo "X720 Shutting down..."

while [ 1 ]; do
shutdownSignal=$(cat /sys/class/gpio/gpio$SHUTDOWN/value)
if [ $shutdownSignal = 0 ]; then
/bin/sleep 0.2
else
pulseStart=$(date +%s%N | cut -b1-13)
while [ $shutdownSignal = 1 ]; do
/bin/sleep 0.02
if [ $(($(date +%s%N | cut -b1-13)-$pulseStart)) -gt $REBOOTPULSEMAXIMUM ]; then
echo "X720 Shutting down", SHUTDOWN, ", halting Rpi ..."
sudo poweroff
exit
fi
shutdownSignal=$(cat /sys/class/gpio/gpio$SHUTDOWN/value)
done
if [ $(($(date +%s%N | cut -b1-13)-$pulseStart)) -gt $REBOOTPULSEMINIMUM ]; then
echo "X720 Rebooting", SHUTDOWN, ", recycling Rpi ..."
sudo reboot
exit
fi
fi
done
