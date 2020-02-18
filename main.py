'''
Created on 26.09.2016

@author: Florian
'''

import os.path
import time
#import SLDO as SLDO
#import plot
from basil.dut import Dut
import SLDO as SLDO
import Xray_auto as XRay


#===============================================================================
# def measure(run_number = 0):
# #    run_number = 0 #SET +1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     
#     flavor='IV' #switch Vin!!
#     filepath = "/Xray_warm/"  + "/" + flavor
#     
#     if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
#         os.makedirs(os.path.normpath(os.getcwd() + filepath))
#     os.chdir(os.path.normpath(os.getcwd() + filepath))
#     
#     iv = SLDO.IV()
#     iv.measure_temp()
#     iv.scan_IV("IV", 1.2, 1, 50, 0.025, run_number=run_number, remote_sense=False)
#     time.sleep(5)
#     iv.scan_load_reg("LoadReg", 0.6, 0.6, 50, 0.025, run_number = run_number)
#     iv.working_point()
#===============================================================================
def measure(run_number = 0):
    dut.init()
    
    iv = SLDO.IV(dut = dut)
    iv.measure_temp()
    iv.scan_IV("IV", 1., 1, 50, 0.025, run_number=run_number, remote_sense=False)
    time.sleep(5)
    iv.scan_load_reg("LoadReg", 0.6, 0.6, 50, 0.025, run_number = run_number)
    iv.working_point(0.5)

    dut.close()
    
def irradiate(current = 51, timer = 60):
    machine.init()
    xray = XRay.Xray(dut = machine)

    xray.set_tube(current, timer)

    machine.close()
    
dut = Dut('devices.yaml')
machine = Dut("xray.yaml")

flavor='IV' #switch Vin!!
filepath = "/Xray_warm/"  + "/" + flavor

if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
    os.makedirs(os.path.normpath(os.getcwd() + filepath))
os.chdir(os.path.normpath(os.getcwd() + filepath))
#measure(run_number= 2)


irradiate(51, 2640)
measure(24)