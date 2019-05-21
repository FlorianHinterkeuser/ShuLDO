'''
Created on 26.09.2016

Misc. script containing the methods used in remote operation of Keithley (source-)meters

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import os.path
import numpy as np

from basil.dut import Dut
from pyexpat import model

class Misc(object):
    
    def __init__(self, dut, max_current=1, minimum_delay=0.1):
        self.max_current = max_current
        self.minimum_delay = minimum_delay
        self.dut = dut
        self.data = []
        self.typ = None
        
        
    
    
    def get_device_type(self, *device):
        '''
        Query device name. get_name() output looks like:
        KEITHLEY INSTRUMENTS INC.,MODEL 2410,1239506,C30   Mar 17 2006 09:29:29/A02  /H/J
        Extract vendor and model id to verify the meter specified in the devices.yaml.
        If needed, the used meters have to be added here (and/or in the devices.yaml).
        
        Currently not in use.
        '''
        name_arr = [None]*len(device)
        type_arr = [None]*len(device)
        vendor = [None]*len(device)
        model = [None]*len(device)
        self.typ = [None]*len(device)
        for i in range(0, len(device)):
            name_arr[i] = str(self.dut[device[i]].get_name())
            if 'Keithley' in name_arr[i] or 'KEITHLEY' in name_arr[i]:
                vendor[i]= 'keithley'
                if 'Model 2410' in name_arr[i] or "MODEL 2410" in name_arr[i]:
                    model[i] = str(2410)
                elif 'Model 2400' in name_arr[i] or "MODEL 2400" in name_arr[i]:
                    model[i] = str(2400)
                elif 'Model 2000' in name_arr[i] or "MODEL 2000" in name_arr[i]:
                    model[i] = str(2000)
                elif 'Model 2602A' in name_arr[i]:
                    model[i] = str(2602) + "A"
                elif 'Model 2230G' in name_arr[i]:
                    model[i] = str(2230) + 'G'
                elif 'Model 2634B' in name_arr[i]:
                    model[i] = str(2634) + 'B'
            else:
                #raise RuntimeError('Something went wrong')
                pass
            self.typ [i] = vendor[i] + '_' + model[i]
            
        return self.typ
          
    def measure_current(self, channel, *device):
        '''
        Current reading of a Keithley 2410 sourcemeter. Since querying the voltage/current reading results in a tuple,
        the proper element has to be selected. In case of the Keithley 2410 sourcemeter, the current reading is the second
        element of the tuple, the voltage reading the first element. If using a different (source-)meter, edit as needed.
        '''
        
        self.get_device_type(*device)
        number = 20
        current = [0.0, 0.0]
        measurement = np.empty(number)
        for i in range(0, len(device)):
            if self.typ[i] == 'keithley_2410' or self.typ[i] == 'keithley_2400' or self.typ[i] == 'keithley_2410':
                for j in range(0, number):
                    measurement[j] = float(self.dut[device[i]].get_current().split(',')[1])
            elif self.typ[i] == 'keithley_2602A' or self.typ[i] == 'keithley_2634B':
                for j in range(0, number):
                    measurement[j] = float(self.dut[device[i]].get_current(channel=channel))
            elif self.typ[i] == 'keithley_2230G':
                for j in range(0, number):
                    measurement[j] = float(self.dut[device[i]].get_current(channel=channel))
            else:
                raise ValueError
            current[0] = np.mean(measurement)
            current[1] = np.std(measurement)
        return current
        

    def measure_voltage(self, channel, *device):
        '''
        See get_current_reading().
        '''
        self.get_device_type(*device)
        number = 20
        voltage = [0.0, 0.0]
        measurement = np.empty(number)
        i = 0

        if self.typ[i] == 'keithley_2410' or self.typ[i] == 'keithley_2000':
            for j in range(0, number):
                measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                while measurement[j] == 0:
                    measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                    if measurement[j] != 0:
                        break
        elif self.typ[i] == 'keithley_2602A' or self.typ[i] == 'keithley_2634B':
            for j in range(0, number):
                measurement[j] = float(self.dut[device[i]].get_voltage(channel=channel).split(',')[0])
                while measurement[j] == 0:
                    measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                    if measurement[j] != 0:
                        break
        elif self.typ[i] == 'keithley_2230G':
            for j in range(0, number):
                measurement[j] = float(self.dut[device[i]].get_voltage(channel=channel).split(',')[0])
                while measurement[j] == 0:
                    measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                    if measurement[j] != 0:
                        break
        elif self.typ[i] == 'keithley_2400':
            for j in range(0, number):
                measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                self.dut[device[i]].set_voltage_limit(2)
                while measurement[j] == 0:
                    measurement[j] = float(self.dut[device[i]].get_voltage().split(',')[0])
                    if measurement[j] != 0:
                        break
                self.dut[device[i]].set_voltage_limit(2)
        else:
            raise ValueError
        voltage[0] = np.mean(measurement)
        voltage[1] = np.std(measurement)
        return voltage
        
    
    def set_source_mode(self, mode, channel, *device):
        '''
        Set the sourcing mode of the Sourcemeter. If needed, additional compliance limits (limit4 - limitn) have to be added.
        '''
        self.get_device_type(*device)
        set_mode = [None]*len(device)
        for i in range(0, len(device)):
            if self.typ[i] == 'keithley_2410' or self.typ[i] == 'keithley_2400' or self.typ[i] == 'keithley_2410':            
                self.dut[device[i]].off()
                set_mode [i] = str(self.dut[device[i]].get_source_mode())
                if 'VOLT' in set_mode[i]:
                    self.dut[device[i]].set_current_limit(0.01)
                    self.dut[device[i]].set_voltage(0)  
                elif 'CURR' in set_mode[i]:
                    self.dut[device[i]].set_voltage_limit(0.01)
                    self.dut[device[i]].set_current(0) 
                else:
                    raise RuntimeError('Something went wrong 1')
                if 'VOLT' in mode:
                        self.dut[device[i]].source_volt()
                        self.dut[device[i]].set_voltage(0)
                        self.dut[device[i]].set_current_limit(0.001)                
                elif 'CURR' in mode:
                        self.dut[device[i]].source_current()
                        self.dut[device[i]].set_voltage_limit(0.01)
                        self.dut[device[i]].set_current(0)
                set_mode [i] = str(self.dut[device[i]].get_source_mode())
            elif self.typ[i] == 'keithley_2602A' or self.typ[i] == 'keithley_2634B':
                if 'VOLT' in mode:
                    self.dut[device[i]].source_volt(channel=channel)
                elif 'CURR' in mode:
                    self.dut[device[i]].source_current(channel=channel)
            elif self.typ[i] == 'keithley_2230G':
                if 'VOLT' in mode:
                    self.dut[device[i]].source_volt(channel=channel)
                elif 'CURR' in mode:
                    self.dut[device[i]].source_current(channel=channel)     
        return set_mode
    
    def reset(self, channel, *device):
        '''Resetting the devices used. The sourcing function currently used should be given as 'mode'. Sets the compliance limit to 1 (mV // mA) and turns the output off.'''
        self.get_device_type(*device)
        set_mode = [None]*len(device)
        for i in range(0, len(device)):
            if self.typ[i] == 'keithley_2410' or self.typ[i] == 'keithley_2400' or self.typ[i] == 'keithley_2410':
                self.dut[device[i]].four_wire_off()
                self.dut[device[i]].set_autorange()
                set_mode[i] = str(self.dut[device[i]].get_source_mode())
                if 'VOLT' in set_mode[i]:
                    self.dut[device[i]].set_current_limit(0.001)
                    self.dut[device[i]].set_voltage(0)  
                elif 'CURR' in set_mode[i]:
                    self.dut[device[i]].set_voltage_limit(0.01)
                    self.dut[device[i]].set_current(0)
                else:
                    return 'False'
                self.dut[device[i]].off()
            elif self.typ[i] == 'keithley_2602A' or self.typ[i] == 'keithley_2634B':
                self.dut[device[i]].reset(channel=channel)
            elif self.typ[i] == 'keithley_2230G':
                self.dut[device[i]].reset(channel=channel)
            else:
                     raise RuntimeWarning
        return set_mode

    def dummy(self,n):
        import random
        random.seed(n)
        number = random.randint(0,20)
        return number
            
    

if __name__ == '__main__':
    
    '''
    Test section
    '''
    dut = Dut('periphery.yaml')
    dut.init()

    misc = Misc(dut=dut)
#    misc.reset(1, 'Sourcemeter1')                       #misc.reset(channel, device*)
#    misc.reset(2, 'Sourcemeter1')
#    misc.reset(1, 'Sourcemeter2')

#    dut['Sourcemeter1'].get_voltage(channel = 2)

#    misc.reset(1, 'Sourcemeter1')                       #misc.reset(channel, device*)
#    misc.reset(2, 'Sourcemeter1')
#    misc.reset(1, 'Sourcemeter2')
