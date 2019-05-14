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

from scan_misc import Misc
from basil.dut import Dut
start = time.clock()
chip_id='RD53B_SLDO_BN001'
flavor='IV' #switch Vin!!
filepath = "/output/" + chip_id + "/" + flavor
fileName = flavor + "_" + chip_id + "_"
if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
    os.makedirs(os.path.normpath(os.getcwd() + filepath))
os.chdir(os.path.normpath(os.getcwd() + filepath))
print os.getcwd()
iv = SLDO.IV()
iv.shutdown_tti()
for i in range(0,1):
    iv.scan_IV(fileName, 2, 1, 200, 0.01, run_number = i, remote_sense= False)

#    iv.current_mirror(fileName, 2, 1, 200, 0.01, run_number = i, remote_sense = False, force_bandgap= True)
    
#    iv.scan_current_balancing(fileName, 2.5, 1, 200, 0.01, run_number = i, remote_sense= False)

#    iv.scan_current_balancing_doublechip(file_name = fileName, max_Iin=5, inputPolarity=1, steps=499, stepSize=0.01, run_number = i, remote_sense = False, invert = True)

#    iv.scan_load_reg(fileName, 0.6, 0.61, 100, 0.01, run_number = i)
iv.working_point()
iv.shutdown_tti()
stop = time.clock()
runtime = stop-start
print "Runtime: %f" % runtime

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