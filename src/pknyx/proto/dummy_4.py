# -*- coding: utf-8 -*-

import time

from pknyx.api import Device, Stack, ETS

GAD_MAP = {1: {'root': "heating",
               1: {'root': "setpoint",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  },
               2: {'root': "temperature",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  }
              },
           2: {'root': "lights",
               1: {'root': None,
                   1: 'living',
                 },
               2: {'root': "etage",
                   1: None,
                   2: "bedroom 1"
                 }
              }
          }


class Lights(Device):

    # Datapoints (= Group Objects) definition
    DP_01 = dict(name="lights_annexe", dptId="1.001", flags="CWTU", priority="low", defaultValue=0.)

    DESC = "Lumières"


stack = Stack()   # Borg
ets = ETS(stack)  # Borg
ets.gadMap = GAD_MAP

lights = Lights(name="lights", desc="Test état lumières", address="1.1.1")

ets.register(lights)

ets.link(dev=lights, dp="lights_annexe", gad=("6/0/8", "6/1/8"))

ets.printMapTable(by="gad")
print
print
ets.printMapTable(by="dp")
print
print

stack.start()
while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        stack.stop()
        break
