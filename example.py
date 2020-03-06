#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# Test version by Charlotte Perry
# ------------------------------------------------------------
#
from basil.dut import Dut
import time
import SLDO as SLDO
# import os

# Talk to a Keithley device via serial port using pySerial
dut = Dut('devices.yaml')
dut.init()

dut['VDD1'].set_current_limit(0.6)

dut['Sourcemeter1'].set_beeper(0)
dut['Sourcemeter2'].set_beeper(0)
dut['Sourcemeter3'].set_beeper(0)
print(dut['Sourcemeter1'].get_name())
print(dut['Sourcemeter2'].get_name())
dut['Sourcemeter1'].source_current(channel=2)
dut['Sourcemeter1'].set_current_range(1e-9, channel=2)
dut['Sourcemeter1'].set_current(0, channel=2)
dut['Sourcemeter1'].set_current_limit(100, channel=2)
dut['Sourcemeter1'].on(channel=2)
for i in range(0, 2):
    voltage = dut['Sourcemeter1'].get_voltage(channel=2)
    print(voltage)

#===============================================================================
# 
# def measure(run_number=0):
#     dut.init()
# 
#     iv = SLDO.IV(dut=dut)
#     # iv.measure_temp()
#     iv.scan_IV("IV", 1., 1, 10, 0.05,
#                run_number=run_number, remote_sense=False)
#     time.sleep(5)
#     # iv.scan_load_reg("LoadReg", 0.6, 0.6, 50, 0.025, run_number=run_number)
#     iv.working_point(0.5)
# 
#     dut.close()
# 
# measure(run_number=0)
#===============================================================================
