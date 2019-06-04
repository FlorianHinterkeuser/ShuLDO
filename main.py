'''
Created on 26.09.2016

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import os.path
import threading
import numpy as np
import plot as plot
#from RD53A_IV import IV
#import RD53A_IV
import SLDO as SLDO
import plot

from scan_misc import Misc
from basil.dut import Dut
start = time.clock()
chip_id='test'
flavor='Temperatur' #switch Vin!!
flavor2 = 'Temp_IV'
filepath = "/output/" + chip_id + "/" + flavor
fileName = flavor2 + "_" + chip_id + "_"
if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
    os.makedirs(os.path.normpath(os.getcwd() + filepath))
os.chdir(os.path.normpath(os.getcwd() + filepath))
iv = SLDO.IV()
iv.shutdown_tti()
n_runs = 1
for i in range(0,n_runs):
    iv.scan_IV(fileName, 2, 1, 200, 0.005, run_number=i, remote_sense=False, OVP_on=False)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense= False, OVP_on=True, OVP_limit=0.45)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense=False, OVP_on=True, OVP_limit=0.475)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense= False, OVP_on=True, OVP_limit=0.5)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense=False, OVP_on=True, OVP_limit=0.525)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense= False, OVP_on=True, OVP_limit=0.55)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense=False, OVP_on=True, OVP_limit=0.575)
    #iv.scan_IV2(fileName, 2, 1, 50, 0.02, run_number = i, remote_sense= False, OVP_on=True, OVP_limit=0.6)
iv.working_point()
iv.shutdown_tti()
stop = time.clock()
runtime = stop-start
Plot = plot.Chip_overview()
Plot.create_iv_overview(chip_id, flavor, '')
#===============================================================================
# def FileAuf(filename):
#     print filename
#     logging.info("auf")
#     with open(filename, 'wb') as outfile:
#         f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
#         f.writerow(['Input current [A]', 'Input voltage [V]', 'Output voltage [V]'])
#     
# for i in range(0,10):
#     FileAuf(filename = "test" + str(i))
#===============================================================================
