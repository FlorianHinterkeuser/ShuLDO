'''
Created on 26.09.2016

@author: Florian
'''

import os.path
import time
from basil.dut import Dut
import SLDO as SLDO


def measure(run_number = 0):
    dut.init()
    
    iv = SLDO.IV(dut = dut)
    iv.measure_temp()
    iv.scan_IV("IV", 1., 1, 50, 0.025, run_number=run_number, remote_sense=False)
    time.sleep(5)
    iv.scan_load_reg("LoadReg", 0.6, 0.6, 50, 0.025, run_number = run_number)
    iv.working_point(0.5)

    dut.close()
    
dut = Dut('devices.yaml')

flavor='IV' #switch Vin!!
filepath = 'output'

if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
    os.makedirs(os.path.normpath(os.getcwd() + filepath))
os.chdir(os.path.normpath(os.getcwd() + filepath))

measure(0)