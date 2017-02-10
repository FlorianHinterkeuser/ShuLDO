'''
Created on 10.02.2017

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import progressbar
import os.path
import numpy as np
from Plot import Plot

from scan_misc import Misc
from basil.dut import Dut

class Dropout(object):
    def scan_Dropout(self, file_name, max_Vin, polarity, steps , stepsize, load, *device):
        '''
        Text, der schlau klingt.
        '''
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        misc.reset(*device)                                          #resetting the Sourcemeters
        
        dut['Sourcemeter1'].four_wire_on()
        dut['Sourcemeter2'].four_wire_on()
        
        misc.set_source_mode('VOLT', 0.5, 0.5, 0.5, 'Sourcemeter1')          #set current source mode for every sourcemeter
        misc.set_source_mode('CURR', 1.5, 1.5, 1.5, 'Sourcemeter2')
        dut['Sourcemeter1'].set_autorange()
        dut['Sourcemeter2'].set_autorange()

        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
        input = 0    
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]'])                      #What is written in the output file
            dut['Sourcemeter2'].set_current(polarity*load)
            
            for step in steps:                                                                                                                      #loop over steps                                                                
                time.sleep(0.01)
                dut['Sourcemeter1'].set_voltage(input)
                time.sleep(0.01)                                                                                                  #Set input voltage
                input_current = misc.measure_current('Sourcemeter1')[0]
                time.sleep(0.01)                                                                                          #Value of interest is in the [0] position of the readout list
                input_voltage = misc.measure_voltage('Sourcemeter1')[0]
                output_voltage_1 = misc.measure_voltage('Sourcemeter2')[0]
                output_current_1 = misc.measure_current('Sourcemeter2')[0]
                time.sleep(0.01)
                logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1 output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 1 load current is %r V" % output_current_1)
                misc.data.append([input_voltage, input_current, output_voltage_1])                                                          #Writing readout in output file
                f.writerow(misc.data[-1])
                input += stepsize                                                                                                                               #Increase input current for next iteration
                if input >= max_Vin or float(input_current) >= 1:                                                                                                #Maximum values reached?
                    break             
            misc.reset(*device)
            
            
if __name__ == '__main__':
    
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)                                                                                                                                     #Calling scan_misc with dut = Dut('devices.yaml')
    
    #print dut['Sourcemeter1'].get_name()                                                                                                                        #Get meter ID to check communication
    #print dut['Sourcemeter2'].get_name()
    #print dut['Sourcemeter3'].get_name()
  
    iv = Dropout()
