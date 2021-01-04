###############################################################################################################
#
# This script will register the ModBus2KNX Gateway as a daemon process executed at system startup.
# This script needs to be rerun everytime the configuration is changed.
# Author: MBizm [https://github.com/MBizm]
#
###############################################################################################################

# set up folder for error log
mkdir ~/.knx/modbus
# copy configuration
cp CONFIG.yaml ~/.knx/modbus/CONFIG.yaml
echo "Updated daemon configuration file: ~/.knx/modbus/CONFIG.yaml"
# copy daemon script
sudo cp ModBusDaemon.py /usr/bin/ModBusDaemon.py
# copy service definition
sudo cp ModBusDaemon.service /lib/systemd/system/ModBusDaemon.service

# reload systemctl daemon
sudo systemctl daemon-reload
# enable at system startup
sudo systemctl enable ModBusDaemon.service
sudo systemctl start ModBusDaemon.service

# wait for system to reload
sleep 10s

# show status
sudo systemctl status ModBusDaemon.service