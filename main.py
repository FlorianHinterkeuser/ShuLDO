'''
Created on 26.09.2016

@author: Florian
'''

import os.path
import time
import SLDO as SLDO
import plot

run_number = 2 #SET +1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

chip_id='BN016'
flavor='IV' #switch Vin!!
filepath = "/output/" + chip_id + "/" + flavor
fileName = "IV"

if not os.path.exists(os.path.normpath(os.getcwd() + filepath)):
    os.makedirs(os.path.normpath(os.getcwd() + filepath))
os.chdir(os.path.normpath(os.getcwd() + filepath))

iv = SLDO.IV()
iv.shutdown_tti()

#iv.current_mirror(fileName, 1.2, 1, 100, 0.02, run_number=run_number)
iv.scan_IV(fileName, 1.2, 1, 100, 0.02, run_number=run_number, remote_sense=False, OVP_on=True, OVP_limit=0.4)
time.sleep(600)
iv.scan_IV(fileName, 1.2, 1, 100, 0.02, run_number=run_number, remote_sense=False, OVP_on=True, OVP_limit=0.45)
time.sleep(600)
iv.scan_IV(fileName, 1.2, 1, 100, 0.02, run_number=run_number, remote_sense=False, OVP_on=True, OVP_limit=0.5)
time.sleep(600)
iv.scan_IV(fileName, 1.2, 1, 100, 0.02, run_number=run_number, remote_sense=False, OVP_on=True, OVP_limit=0.55)
time.sleep(600)
iv.scan_IV(fileName, 1.2, 1, 100, 0.02, run_number=run_number, remote_sense=False, OVP_on=True, OVP_limit=0.6)
time.sleep(600)
iv.scan_load_reg(fileName, iin = 0.6, max_iload = 0.6, steps = 50, stepSize = 0.03,run_number=run_number)

#iv.working_point()
iv.shutdown_tti()
#Plot = plot.Chip_overview()
#Plot.create_iv_overview(chip_id, flavor, str(run_number) + '_' + fileName + '_LineReg')
#Plot.create_iv_overview(chip_id, flavor, str(run_number) + '_' + fileName + '_LoadReg')
