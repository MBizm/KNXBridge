###############################################################################################################
#
# This script will register the KNXBridge as a daemon process executed at system startup.
# This script needs to be rerun everytime the configuration is changed.
# Author: MBizm [https://github.com/MBizm]
#
###############################################################################################################

# set up folder for error log
mkdir ~/.knx
mkdir ~/.knx/bridge
# copy configuration
cp CONFIG.yaml ~/.knx/bridge/CONFIG.yaml
echo "Updated daemon configuration file: ~/.knx/bridge/CONFIG.yaml"
# copy daemon script
sudo mkdir /usr/bin/KNXBridge
sudo cp core /usr/bin/KNXBridge
# copy service definition
sudo cp KNXBridgeDaemon.service /lib/systemd/system/KNXBridgeDaemon.service

# reload systemctl daemon
sudo systemctl daemon-reload
# enable at system startup
sudo systemctl enable KNXBridgeDaemon.service
sudo systemctl start KNXBridgeDaemon.service

# wait for system to reload
sleep 10s

# show status
sudo systemctl status KNXBridgeDaemon.service