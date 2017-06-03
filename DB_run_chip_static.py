'''
Created on 26.09.2016

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
        self.maximumInputCurrent = 0.0  #for a single regulator
    
    def run_CURR(self, Iin, inputPolarity):
        
        if float(self.maximumInputCurrent) < float(Iin):
            print "ERROR: maximumInputCurrent < Iin"
            return
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Iload1
        misc.reset(1, 'Sourcemeter2')   #Iload2
        #
        misc.reset(1, 'Sourcemeter3')   #Vshunt1
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        dut['Sourcemeter3'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2)
        dut['Sourcemeter3'].set_voltage_limit(0.02)
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        dut['Sourcemeter2'].set_current(0)
        #dut['Sourcemeter3'].on()
        dut['Sourcemeter3'].set_current(0)
        
        dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1)   #set Iin
        
        iv.loop_CURR(Iin)
    
    def run_VOLT(self, Vin, inputPolarity):
        
        if float(Vin) > 1.99:
            print "ERROR: Vin > 1.99V"
            return
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Vin
        misc.reset(2, 'Sourcemeter1')   #Iload1
        misc.reset(1, 'Sourcemeter2')   #Iload2
        #
        misc.reset(1, 'Sourcemeter3')   #Vshunt1
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        dut['Sourcemeter3'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(0.05, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2)
        dut['Sourcemeter3'].set_voltage_limit(0.02)
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(6, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        dut['Sourcemeter2'].set_current(0)
        #dut['Sourcemeter3'].on()
        dut['Sourcemeter3'].set_current(0)
        
        dut['Sourcemeter1'].set_voltage(inputPolarity*Vin, channel=1)   #set Vin
        
        iv.loop_VOLT()
    
    def loop_CURR(self, I_in):
        V_in = misc.measure_voltage(1, 'Sourcemeter1')[0]
        V_out1 = misc.measure_voltage(2, 'Sourcemeter1')[0]
        V_out2 = misc.measure_voltage(1, 'Sourcemeter2')[0]
        I_in1 = (1/0.01)*misc.measure_voltage(1, 'Sourcemeter3')[0]
        I_in2 = I_in-I_in1
        print "Vin: "+str(V_in)+"V\t\t"+"Vout1: "+str(V_out1)+"V\t\t"+"Vout2: "+str(V_out2)
        if float(V_in) > 1.99:
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Vin reached maximum value (1.99V)!"
            return
        elif float(I_in1) > float(self.maximumInputCurrent):
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Iin1 reached maximum value ("+str(self.maximumInputCurrent)+"A)!"
            return
        elif float(I_in2) > float(self.maximumInputCurrent):
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Iin2 reached maximum value ("+str(self.maximumInputCurrent)+"A)!"
            return
        time.sleep(2)
        iv.loop_CURR(I_in)
    
    def loop_VOLT(self):
        I_in = misc.measure_current(1, 'Sourcemeter1')[0]
        V_out1 = misc.measure_voltage(2, 'Sourcemeter1')[0]
        V_out2 = misc.measure_voltage(1, 'Sourcemeter2')[0]
        print "Iin: "+str(I_in)+"V\t\t"+"Vout1: "+str(V_out1)+"V\t\t"+"Vout2: "+str(V_out2)
        if float(I_in) > 0.05:
            misc.reset(1, 'Sourcemeter1')
            misc.reset(2, 'Sourcemeter1')
            misc.reset(1, 'Sourcemeter2')
            misc.reset(1, 'Sourcemeter3')
            print "ERROR: Iin reached maximum value ("+str(0.05)+"A)!"
            return
        time.sleep(2)
        iv.loop_VOLT()


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
    
    #iv.run_CURR(Iin, inputPolarity):
    iv.run_CURR(0.8,  1)
    
#    #iv.run_VOLT(Vin, inputPolarity):
#    iv.run_VOLT(1.4,  1)
