import paho.mqtt.client as mqtt

from core.ApplianceBase import ApplianceBase
from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log


class MQTTAppliance(ApplianceBase):
    def __init__(self, host,
                 port=None, user=None, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = passwd

    def getName(self) -> str:
        return "MQTT Appliance"

    def setAttribute(self, attr, val, function):
        """
        custom implementation to suit *2mqtt requests
        will update the define attribute on the MQTT broker
        """
        # setup temporary client for one-time request
        client = _MQTTBaseClient(self.host, self.port, self.user, self.pwd, attr)
        client.setAttribute(attr, val, function)
        client.closeConnection()

    def setupClient(self, name, topic, knxAddr, knxFormat, mqttFormat=None, function=None, flags=None):
        client = _MQTT2KNXClient(self.host, self.port, self.user, self.pwd,
                                 name, topic, mqttFormat,
                                 knxAddr, knxFormat, function, flags)
        client.start()


class _MQTTBaseClient(KNXDDevice):
    def __init__(self, host, port, user, passwd, name):
        super(_MQTTBaseClient, self).__init__()

        # set up MQTT client connection to broker
        self.client = mqtt.Client("KNXBridgeDaemon-" + name)

        # authenticate
        if user and passwd:
            self.client.username_pw_set(username=user,
                                        password=passwd)
        elif user:
            self.client.username_pw_set(username=user)

        try:
            # establish connection
            if host and port:
                self.client.connect(host=host, port=port)
            else:
                self.client.connect(host=host)
        except ConnectionRefusedError as ex:
            log('error',
                'Could not connect to MQTT server {0} port {1} [{2}]'.format(host,
                                                                             port,
                                                                             ex))

        def setAttribute(self, attr, val, function):
            raise NotImplementedError

    def setAttribute(self, attr, val, function):
        """
        updates value on broker
        """
        self.client.publish(attr, val)

    def closeConnection(self):
        self.client.disconnect()


class _MQTT2KNXClient(_MQTTBaseClient):
    """
    client class which initiates a listener threads which reports any chage from the broker
    via the callback function
    """

    def __init__(self, host, port, user, passwd,
                 name, topic, mqttFormat,
                 knxDest, knxFormat, function, flags):
        super(_MQTT2KNXClient, self).__init__(host, port, user, passwd, name)

        self.attrName = name
        self.mqttFormat= mqttFormat
        self.knxDest = knxDest
        self.knxFormat = knxFormat
        self.function = function
        self.flags = flags

        try:
            # listener target/endpoint
            self.client.on_message = self.updateReceived

            self.client.subscribe(topic)
        except ValueError as ex:
            log('error',
                'Could not connect to MQTT server {0} for endpoint {1} [{2}]'.format(host,
                                                                                     topic,
                                                                                     ex))

    def start(self):
        self.client.loop_start()

    def updateReceived(self, client, userdata, message):
        val = message.payload.decode("utf-8")

        if self.mqttFormat == 'int':
            val = int(val)
        elif self.mqttFormat == 'float':
            val = float(val)
        elif self.mqttFormat == 'boolean':
            if val == 'True':
                val = True
            elif val == 'False':
                val = False
        elif self.mqttFormat == 'str':
            val = str(val)

        super().writeKNXAttribute(self.attrName, self.knxDest, self.knxFormat,
                                  val, function=self.function, flags=self.flags)
