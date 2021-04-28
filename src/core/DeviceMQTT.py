import paho.mqtt.client as mqtt

from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log


class MQTTAppliance():
    def __init__(self, host,
                 port=None, user=None, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = passwd

    def setupClient(self, name, topic, knxAddr, knxFormat, function=None, flags=None):
        client = _MQTTClient(self.host, self.port, self.user, self.pwd,
                             name, topic,
                             knxAddr, knxFormat, function, flags)
        client.start()


class _MQTTClient(KNXDDevice):
    """
    client class which initiates a listener threads which reports any chage from the broker
    via the callback function
    """
    def __init__(self, host, port, user, passwd,
                 name, topic,
                 knxDest, knxFormat, function, flags):
        super(_MQTTClient, self).__init__()

        self.attrName = name
        self.knxDest = knxDest
        self.knxFormat = knxFormat
        self.function = function
        self.flags = flags

        # set up MQTT client connection to broker
        self.client = mqtt.Client("KNXBridgeDaemon")
        self.client.on_message = self.updateReceived
        # authenticate
        if user and passwd:
            self.client.username_pw_set(username=user,
                                        password=passwd)
        elif user:
            self.client.username_pw_set(username=user)
        # establish connection
        if host and port:
            self.client.connect(host=host, port=port)
        else:
            self.client.connect(host=host)
        # listener target/endpoint
        try:
            self.client.subscribe(topic)
        except ValueError as ex:
            log('error',
                'Could not connect to MQTT server {0} for endpoint {1} [{2}]'.format(host,
                                                                                     topic,
                                                                                     ex))

    def start(self):
        self.client.loop_start()

    def updateReceived(self, client, userdata, message):
        super().writeKNXAttribute(self.attrName, self.knxDest, self.knxFormat,
                                  float(message.payload.decode("utf-8")), function=self.function, flags=self.flags)
