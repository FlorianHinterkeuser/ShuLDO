'''
Created on 24.05.2017

@author: Florian, Markus
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import os.path
import numpy as np

from scan_misc import Misc
from basil.dut import Dut

class IV(object):
    
    '''
    Class to perform a standard IV scan of the FE65 ShuLDO.
    '''
    
    def __init__(self):
        """A constructor"""
        self.maximumInputCurrent = 0.0
    
    def run_CURR(self, Iin, inputPolarity, Vref, Voff):
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Iload
        #
        misc.reset(1, 'Sourcemeter2')   #Vref
        misc.reset(1, 'Sourcemeter3')   #Voff
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        #
        misc.set_source_mode('VOLT', 1, 'Sourcemeter2')
        misc.set_source_mode('VOLT', 1, 'Sourcemeter3')
        
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)
        
        
        #Set compliance limits
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        #
        dut['Sourcemeter2'].set_current_limit(0.001)
        dut['Sourcemeter3'].set_current_limit(0.001)
        
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter1'].set_current_range(0.01, channel = 2)
        #
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #
        dut['Sourcemeter2'].set_voltage(Vref)   #set Vref
        dut['Sourcemeter3'].set_voltage(Voff)   #set Voff
        #
        dut['Sourcemeter2'].on()
        dut['Sourcemeter3'].on()
        
        dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1) #set Iin
        
        iv.loop_CURR(Iin)
    
    def run_VOLT(self, Vin, inputPolarity, Vref, Voff):
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Vin
        misc.reset(2, 'Sourcemeter1')   #Iload
        #
        misc.reset(1, 'Sourcemeter2')   #Vref
        misc.reset(1, 'Sourcemeter3')   #Voff
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        #
        misc.set_source_mode('VOLT', 1, 'Sourcemeter2')
        misc.set_source_mode('VOLT', 1, 'Sourcemeter3')
        
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)
        
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(self.maximumInputCurrent, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        #
        dut['Sourcemeter2'].set_current_limit(0.001)
        dut['Sourcemeter3'].set_current_limit(0.001)
        
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(6, channel = 1)
        dut['Sourcemeter1'].set_current_range(0.01, channel = 2)
        #
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #
        dut['Sourcemeter2'].set_voltage(Vref)   #set Vref
        dut['Sourcemeter3'].set_voltage(Voff)   #set Voff
        #
        dut['Sourcemeter2'].on()
        dut['Sourcemeter3'].on()
        
        dut['Sourcemeter1'].set_voltage(inputPolarity*Vin, channel=1)   #set Vin
        
        iv.loop_VOLT(Vin)
    
    def loop_CURR(self, I_in):
        V_in = misc.measure_voltage(1, 'Sourcemeter1')[0]
        V_out = misc.measure_voltage(2, 'Sourcemeter1')[0]
        print "Iin: "+str(I_in)+"A\t\t"+"Vin: "+str(V_in)+"V\t\t"+"Vout: "+str(V_out)+"V"
        if float(V_in) > 1.99:
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Vin reached maximum value (1.99V)!"
            return
        time.sleep(2)
        iv.loop_CURR(I_in)
    
    def loop_VOLT(self, V_in):
        I_in = misc.measure_current(1, 'Sourcemeter1')[0]
        V_out = misc.measure_voltage(2, 'Sourcemeter1')[0]
        print "Vin: "+str(V_in)+"V\t\t"+"Iin: "+str(I_in)+"A\t\t"+"Vout: "+str(V_out)+"V"
        if float(I_in) > 0.05:
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Iin reached maximum value ("+str(0.05)+"A)!"
            return
        time.sleep(2)
        iv.loop_VOLT(V_in)


if __name__ == '__main__':
    
    #Calling scan_misc with dut = Dut('devices.yaml')
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)
    
    #Get meter ID to check communication
    print 'Sourcemeter 1: '+dut['Sourcemeter1'].get_name()
    print 'Sourcemeter 2: '+dut['Sourcemeter2'].get_name()
    print 'Sourcemeter 3: '+dut['Sourcemeter3'].get_name()
    
    raw_input("Proceed?")
    
    iv = IV()
#    iv.maximumInputCurrent = 1.0    #1A chip
    iv.maximumInputCurrent = 2.0    #2A chip
    
    #iv.run_CURR(Iin, inputPolarity, Vref, Voff):
    iv.run_CURR(1.0,  1,             0.6,  0.8)
    
#    #iv.run_VOLT(Vin, inputPolarity, Vref, Voff):
#    iv.run_VOLT(1.4,  1,             0.6,  0.8)
