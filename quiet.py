#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# Test version by Charlotte Perry
# ------------------------------------------------------------
#
from basil.dut import Dut
# import time

# Talk to a Keithley device via serial port using pySerial
dut = Dut('devices.yaml')
dut.init()

#dut['VDD1'].set_current_limit(0.6)
# time.sleep(1)
#dut['VDD1'].set_enable(on=True)
# time.sleep(1)

devices = ['Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3']
for dev in devices:
    dut[dev].set_beeper(0)

# print(dut['Powersupply'].get_name())

print('hallo')

dut['VDD1'].get_voltage()
