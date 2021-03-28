# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Datapoint Types management

Implements
==========

 - B{DPTXlator4ByteFloat}

Usage
=====

see L{DPTXlatorBoolean}

@todo: handle NaN

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlator4ByteFloat(DPTXlatorBase):
    """ DPTXlator class for 4-Byte-Float (F32) KNX Datapoint Type

     - 2 Byte Float: SEEEEEEE EFFFFFFF FFFFFFFF FFFFFFFF (IEEE 754)
     - S: Sign [0, 1]
     - E: Exponent [0:255]
     - F: Fraction [0:8388607]

    .
    """
    DPT_Generic = DPT("14.xxx", "Generic", (-3.4028234663852886e+38, 3.4028234663852886e+38))
    #DPT_Generic = DPT("14.xxx", "Generic", (-340282346638528859811704183484516925440, 340282346638528859811704183484516925440))

    DPT_Value_Acceleration = DPT("14.000", "Acceleration", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m/s²")
    DPT_Value_Acceleration_Angular = DPT("14.001", "Acceleration, angular", (-3.4028234663852886e+38, 3.4028234663852886e+38), "rad/s²")
    DPT_Value_Activation_Energy = DPT("14.002", "Activation energy", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J/mol")
    DPT_Value_Activity = DPT("14.003", "Activity (radioactive)", (-3.4028234663852886e+38, 3.4028234663852886e+38), "s⁻¹")
    DPT_Value_Mol = DPT("14.004", "Amount of substance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "mol")
    DPT_Value_Amplitude = DPT("14.005", "Amplitude", (-3.4028234663852886e+38, 3.4028234663852886e+38))
    DPT_Value_AngleRad = DPT("14.006", "Angle, radiant", (-3.4028234663852886e+38, 3.4028234663852886e+38), "rad")
    DPT_Value_AngleDeg = DPT("14.007", "Angle, degree", (-3.4028234663852886e+38, 3.4028234663852886e+38), "°")
    DPT_Value_Angular_Momentum = DPT("14.008", "Angular momentum", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J.s")
    DPT_Value_Angular_Velocity = DPT("14.009", "Angular velocity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "rad/s")
    DPT_Value_Area = DPT("14.010", "Area", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m²")
    DPT_Value_Capacitance = DPT("14.011", "Capacitance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "F")
    DPT_Value_Charge_DensitySurface = DPT("14.012", "Charge density (surface)", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C/m²")
    DPT_Value_Charge_DensityVolume = DPT("14.013", "Charge density (volume)", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C/m³")
    DPT_Value_Compressibility = DPT("14.014", "Compressibility", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m²/N")
    DPT_Value_Conductance = DPT("14.015", "Conductance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "S")
    DPT_Value_Electrical_Conductivity = DPT("14.016", "Conductivity, electrical", (-3.4028234663852886e+38, 3.4028234663852886e+38), "S/m")
    DPT_Value_Density = DPT("14.017", "Density", (-3.4028234663852886e+38, 3.4028234663852886e+38), "kg/m³")
    DPT_Value_Electric_Charge = DPT("14.018", "Electric charge", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C")
    DPT_Value_Electric_Current = DPT("14.019", "Electric current", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A")
    DPT_Value_CurrentDensity = DPT("14.020", "Electric current density", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A/m²")
    DPT_Value_Electric_DipoleMoment = DPT("14.021", "Electric dipole moment", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Cm")
    DPT_Value_Electric_Displacement = DPT("14.022", "Electric displacement", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C/m²")
    DPT_Value_Electric_FieldStrength = DPT("14.023", "Electric field strength", (-3.4028234663852886e+38, 3.4028234663852886e+38), "V/m")
    DPT_Value_Electric_Flux = DPT("14.024", "Electric flux", (-3.4028234663852886e+38, 3.4028234663852886e+38), "c")  # unit??? C
    DPT_Value_Electric_FluxDensity = DPT("14.025", "Electric flux density", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C/m²")
    DPT_Value_Electric_Polarization = DPT("14.026", "Electric polarization", (-3.4028234663852886e+38, 3.4028234663852886e+38), "C/m²")
    DPT_Value_Electric_Potential = DPT("14.027", "Electric potential", (-3.4028234663852886e+38, 3.4028234663852886e+38), "V")
    DPT_Value_Electric_PotentialDifference = DPT("14.028", "Electric potential difference", (-3.4028234663852886e+38, 3.4028234663852886e+38), "V")
    DPT_Value_ElectromagneticMoment = DPT("14.029", "Electromagnetic moment", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A.m²")
    DPT_Value_Electromotive_Force = DPT("14.030", "Electromotive force", (-3.4028234663852886e+38, 3.4028234663852886e+38), "V")
    DPT_Value_Energy = DPT("14.031", "Energy", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J")
    DPT_Value_Force = DPT("14.032", "Force", (-3.4028234663852886e+38, 3.4028234663852886e+38), "N")
    DPT_Value_Frequency = DPT("14.033", "Frequency", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Hz")
    DPT_Value_Angular_Frequency = DPT("14.034", "Frequency, angular (pulsatance)", (-3.4028234663852886e+38, 3.4028234663852886e+38), "rad/s")
    DPT_Value_Heat_Capacity = DPT("14.035", "Heat capacity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J/K")
    DPT_Value_Heat_FlowRate = DPT("14.036", "Heat flow rate", (-3.4028234663852886e+38, 3.4028234663852886e+38), "W")
    DPT_Value_Heat_Quantity = DPT("14.037", "Heat quantity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J")
    DPT_Value_Impedance = DPT("14.038", "Impedance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Ohm")
    DPT_Value_Length = DPT("14.039", "Length", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m")
    DPT_Value_Light_Quantity = DPT("14.040", "Light quantity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J")
    DPT_Value_Luminance = DPT("14.041", "Luminance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "cd/m²")
    DPT_Value_Luminous_Flux = DPT("14.042", "Luminous flux", (-3.4028234663852886e+38, 3.4028234663852886e+38), "lm")
    DPT_Value_Luminous_Intensity = DPT("14.043", "Luminous intensity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "cd")
    DPT_Value_Magnetic_FieldStrength = DPT("14.044", "Magnetic field strengh", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A/m")
    DPT_Value_Magnetic_FLux = DPT("14.045", "Magnetic flux", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Wb")
    DPT_Value_Magnetic_FluxDensity = DPT("14.046", "Magnetic flux density", (-3.4028234663852886e+38, 3.4028234663852886e+38), "T")
    DPT_Value_Magnetic_Moment = DPT("14.047", "Magnetic moment", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A.m²")
    DPT_Value_Magnetic_Polarization = DPT("14.048", "Magnetic polarization", (-3.4028234663852886e+38, 3.4028234663852886e+38), "T")
    DPT_Value_Magnetization = DPT("14.049", "Magnetization", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A/m")
    DPT_Value_MagnetomotiveForce = DPT("14.050", "Magnetomotive force", (-3.4028234663852886e+38, 3.4028234663852886e+38), "A")
    DPT_Value_Mass = DPT("14.051", "Mass", (-3.4028234663852886e+38, 3.4028234663852886e+38), "kg")
    DPT_Value_MassFlux = DPT("14.052", "Mass flux", (-3.4028234663852886e+38, 3.4028234663852886e+38), "kg/s")
    DPT_Value_Momentum = DPT("14.053", "Momentum", (-3.4028234663852886e+38, 3.4028234663852886e+38), "N/s")
    DPT_Value_Phase_AngleRad = DPT("14.054", "Phase angle, radiant", (-3.4028234663852886e+38, 3.4028234663852886e+38), "rad")
    DPT_Value_Phase_AngleDeg = DPT("14.055", "Phase angle, degree", (-3.4028234663852886e+38, 3.4028234663852886e+38), "°")
    DPT_Value_Power = DPT("14.056", "Power", (-3.4028234663852886e+38, 3.4028234663852886e+38), "W")
    DPT_Value_Power_Factor = DPT("14.057", "Power factor", (-3.4028234663852886e+38, 3.4028234663852886e+38), "cos phi")
    DPT_Value_Pressure = DPT("14.058", "Pressure", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Pa")
    DPT_Value_Reactance = DPT("14.059", "Reactance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Ohm")
    DPT_Value_Resistance = DPT("14.060", "Resistance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Ohm")
    DPT_Value_Resistivity = DPT("14.061", "Resistivity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Ohm.m")
    DPT_Value_SelfInductance = DPT("14.062", "Self inductance", (-3.4028234663852886e+38, 3.4028234663852886e+38), "H")
    DPT_Value_SolidAngle = DPT("14.063", "Solid angle", (-3.4028234663852886e+38, 3.4028234663852886e+38), "sr")
    DPT_Value_Sound_Intensity = DPT("14.064", "Sound intensity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "W/m²")
    DPT_Value_Speed = DPT("14.065", "Speed", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m/s")
    DPT_Value_Stress = DPT("14.066", "Stress", (-3.4028234663852886e+38, 3.4028234663852886e+38), "Pa")
    DPT_Value_Surface_Tension = DPT("14.067", "Surface tension", (-3.4028234663852886e+38, 3.4028234663852886e+38), "N/m")
    DPT_Value_Common_Temperature = DPT("14.068", "Temperature, common", (-3.4028234663852886e+38, 3.4028234663852886e+38), "°C")
    DPT_Value_Absolute_Temperature = DPT("14.069", "Temperature, absolute", (-3.4028234663852886e+38, 3.4028234663852886e+38), "K")
    DPT_Value_TemperatureDifference = DPT("14.070", "Temperature difference", (-3.4028234663852886e+38, 3.4028234663852886e+38), "K")
    DPT_Value_Thermal_Capacity = DPT("14.071", "Thermal capacity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J/K")
    DPT_Value_Thermal_Conductivity = DPT("14.072", "Thermal conductivity", (-3.4028234663852886e+38, 3.4028234663852886e+38), "W/m/K")
    DPT_Value_ThermoelectricPower = DPT("14.073", "Thermoelectric power", (-3.4028234663852886e+38, 3.4028234663852886e+38), "V/K")
    DPT_Value_Time = DPT("14.074", "Time", (-3.4028234663852886e+38, 3.4028234663852886e+38), "s")
    DPT_Value_Torque = DPT("14.075", "Torque", (-3.4028234663852886e+38, 3.4028234663852886e+38), "N.m")
    DPT_Value_Volume = DPT("14.076", "Volume", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m³")
    DPT_Value_Volume_Flux = DPT("14.077", "Volume flux", (-3.4028234663852886e+38, 3.4028234663852886e+38), "m³/s")
    DPT_Value_Weight = DPT("14.078", "Weight", (-3.4028234663852886e+38, 3.4028234663852886e+38), "N")
    DPT_Value_Work = DPT("14.079", "Work", (-3.4028234663852886e+38, 3.4028234663852886e+38), "J")

    def __init__(self, dptId):
        super(DPTXlator4ByteFloat, self).__init__(dptId, 4)

    def checkData(self, data):
        if not 0x00000000 <= data <= 0xffffffff:
            raise DPTXlatorValueError("data %s not in (0x00000000, 0xffffffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        value = struct.unpack(">f", struct.pack(">L", data))[0]  # struct.unpack(">f", self.toFrame())[0]
        #Logger().debug("DPTXlator4ByteFloat.dataToValue(): value=%f" % value)
        return value

    def valueToData(self, value):
        data = struct.unpack(">L", struct.pack(">f", value))[0]  # self.frameToData(struct.pack(">f", value))
        #Logger().debug("DPTXlator4ByteFloat.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">L", data))

    def frameToData(self, frame):
        data = struct.unpack(">L", str(frame))[0]
        return data


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPT4ByteFloatTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (-340282346638528859811704183484516925440, 0xff7fffff, "\xff\x7f\xff\xff"),
                (                                      -1, 0xbf800000, "\xbf\x80\x00\x00"),
                (                                       0, 0x00000000, "\x00\x00\x00\x00"),
                (                                       1, 0x3f800000, "\x3f\x80\x00\x00"),
                ( 340282346638528859811704183484516925440, 0x7f7fffff, "\x7f\x7f\xff\xff"),
            )
            self.dptXlator = DPTXlator4ByteFloat("14.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 4)

        def testcheckValue(self):
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue(self.dptXlator._dpt.limits[1] * 10)

        def test_dataToValue(self):
            for value, data, frame in self.testTable:
                value_ = self.dptXlator.dataToValue(data)
                self.assertEqual(value_, value, "Conversion failed (converted value for %s is %.f, should be %.f)" %
                                 (hex(data), value_, value))

        def test_valueToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.valueToData(value)
                self.assertEqual(data_, data, "Conversion failed (converted data for %.f is %s, should be %s)" %
                                 (value, hex(data_), hex(data)))

        def test_dataToFrame(self):
            for value, data, frame in self.testTable:
                frame_ = self.dptXlator.dataToFrame(data)
                self.assertEqual(frame_, frame, "Conversion failed (converted frame for %s is %r, should be %r)" %
                                 (hex(data), frame_, frame))

        def test_frameToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.frameToData(frame)
                self.assertEqual(data_, data, "Conversion failed (converted data for %r is %s, should be %s)" %
                                 (frame, hex(data_), hex(data)))

    unittest.main()
