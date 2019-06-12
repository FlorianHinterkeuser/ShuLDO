'''
Created on 26.09.2016
----------------
set timer
start timer
set HV on
open shutter
	get actual time
	scan
set timer
start timer
set HV on
open shutter
etc.
-------------------

'''
import time
import logging
import math
import yaml
from datetime import datetime, timedelta
import csv
import os.path
import threading
import numpy as np

from scan_misc import Misc
from basil.dut import Dut
from ntc_check import current_mirror

def measure_temp():
    temp_log = {}
    ntc = float(dut['Multimeter1'].get_resistance())
    temp = 1/(1./298.15 + 1./3435. * math.log(ntc/10000.))-273.15
    with open('ntc_log.yaml', 'a') as outfile:
        key = str(time.time())
        temp_log[key] = temp
        yaml.dump(temp_log, outfile)
    logging.info('Current temperature is %f C' % temp)

dut = Dut('devices.yaml')
dut.init()
xray = 'xray_cabinet'

t_target = 174000
t_ntc = 300
t_ref = t_target-t_ntc
tube_voltage = 50 #kV
tube_current = 51 #mA

dut[xray].set_voltage(tube_voltage)
dut[xray].set_current(tube_current)
dut[xray].set_timer(1, t_target)
dut[xray].start_timer()
dut[xray].set_highvoltage_on()
time.sleep(15)
dut[xray].open_shutter()
current_time = datetime.now()
delta_time = timedelta(seconds = t_target)
eta = current_time + delta_time

print(dut[xray].get_nominal_voltage())
print(dut[xray].get_nominal_current())
print(dut[xray].get_actual_voltage())
status = dut[xray].get_status(1) # second bit is HV on/off
logging.info('Status is %r' % status)
logging.info('ETA is %r ' % eta)
while True:
    t_actual = dut[xray].get_actual_time()
    if int(t_actual) < t_ref:
        status = dut[xray].get_status(1)
        measure_temp()
        logging.info('Remaining time is %f s' % t_actual)
        logging.info('ETA is %r ' % eta)
        t_ref -= t_ntc
    if int(t_actual) < 2:
        break



current_mirror()
logging.info("Step finished. Please perform measurements.")
logging.info("When done, increase run_number, set target time and tube current to continue.")

