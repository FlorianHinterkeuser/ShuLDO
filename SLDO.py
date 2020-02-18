'''
Created on 26.09.2016

@author: Florian
'''
import logging
import csv
import os.path
import time

from scan_misc import Misc
from basil.dut import Dut

#===============================================================================
# dut = Dut('devices.yaml')
# dut.init()
#===============================================================================

class IV(object):
    def __init__(self, dut):
        self.dut = dut
        self.misc = Misc(dut=self.dut)
    
    '''
    Class to perform a standard IV scan of the RD53A ShuLDO.
    '''    
    def scan_IV(self, file_name, max_Iin, inputPolarity, steps, stepSize, run_number = 0, remote_sense = True, OVP_on = False, OVP_limit = 0.5):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")

        #=======================================================================
        # misc.reset(1, 'Sourcemeter1')   #Vout
        # misc.reset(2, 'Sourcemeter1')   #vref
        # misc.reset(1, 'Sourcemeter2')   #Voff
        # misc.reset(1, 'Sourcemeter3')   #Vrext
        # misc.reset(2, 'Sourcemeter3')   #Iref
        #=======================================================================
 
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter3')  
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter3')     
 
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        self.dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 2)
 
        self.dut['Sourcemeter1'].set_current(0, channel=1)
        self.dut['Sourcemeter1'].set_current(0, channel=2)
        self.dut['Sourcemeter2'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=2)
        
        self.dut['Sourcemeter1'].four_wire_on(channel=1)
        self.dut['Sourcemeter1'].four_wire_off(channel=2)
        self.dut['Sourcemeter2'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=2)
 
        self.dut['Sourcemeter1'].on(channel=1)
        self.dut['Sourcemeter1'].on(channel=2)
        self.dut['Sourcemeter2'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=2)

        fncounter=1
        filename = file_name + str(run_number) + ".csv"
        print("writing to file %s" %filename)
        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Iref [uA]', 'Mirrored Current [V]'])

            self.dut['VDD1'].set_current_limit(0)
            time.sleep(1)
            iin = 0.001
            self.dut['VDD1'].set_voltage(2)
            time.sleep(0.5)
            self.dut['VDD1'].reset_trip()
            time.sleep(0.5)
            self.dut['VDD1'].set_enable(on=True)
            time.sleep(1)
            for x in range(0, int(steps)):
                
                logging.info("Setting Current to %f" % iin)
                self.dut['VDD1'].set_current_limit(iin)
                time.sleep(0.5)

                logging.info("measuring ...")
                input_voltage = self.dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = self.misc.measure_voltage(1, 'Sourcemeter1')[0]
                vref = self.misc.measure_voltage(2, 'Sourcemeter1')[0]
                voff = self.misc.measure_voltage(1, 'Sourcemeter2')[0]
                vrext = self.misc.measure_voltage(1, 'Sourcemeter3')[0]
                iref = float(self.misc.measure_voltage(2, 'Sourcemeter3')[0])/150000
                
                preliminiary_mirrored_current = vrext / 800
                logging.info("Mirrored current is %r A" % preliminiary_mirrored_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("VDD is %r V" % vdd)
                logging.info("Vref is %r V" % vref)
                logging.info("Voffs is %r V" % voff)
                logging.info("Iref is %r V" % iref)



                self.misc.data.append([iin, input_voltage, vdd, vref, voff, iref, vrext])
                f.writerow(self.misc.data[-1])
                
                iin += stepSize
                if float(iin) > float(max_Iin) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        self.measure_temp()
        logging.info('Measurement finished.')

        #=======================================================================
        # misc.reset(1, 'Sourcemeter1')
        # misc.reset(2, 'Sourcemeter1')
        # misc.reset(1, 'Sourcemeter2')
        # misc.reset(1, 'Sourcemeter3')
        # misc.reset(2, 'Sourcemeter3')
        #=======================================================================
        return iin
    
    def scan_load_reg(self, file_name, iin, max_iload, steps, stepSize, run_number = 0):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")
 
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter3')
 
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        self.dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 2)
 
        self.dut['Sourcemeter1'].set_current(0, channel=1)
        self.dut['Sourcemeter1'].set_current(0, channel=2)
        self.dut['Sourcemeter2'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=2)
        
        self.dut['Sourcemeter1'].four_wire_on(channel=1)
        self.dut['Sourcemeter1'].four_wire_off(channel=2)
        self.dut['Sourcemeter2'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=2)
 
        self.dut['Sourcemeter1'].on(channel=1)
        self.dut['Sourcemeter1'].on(channel=2)
        self.dut['Sourcemeter2'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=2)

        fncounter=1
        filename = file_name + str(run_number) + ".csv"
        print("writing to file %s" %filename)
        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Load current [A]', 'Input voltage [V]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Iref [uA]', 'Mirrored Current [V]'])

            self.dut['VDD1'].set_current_limit(iin)
            time.sleep(1)
            iload = 0
            self.dut['VDD1'].set_voltage(1.99)
            time.sleep(0.5)
            self.dut['VDD1'].reset_trip()
            time.sleep(0.5)
            self.dut['VDD1'].set_enable(on=True)
            time.sleep(1)
            for x in range(0, int(steps)):
                
                logging.info("Setting Current")
                self.dut['Sourcemeter1'].set_current(iload, channel=1)
                time.sleep(1)

                logging.info("measuring ...")
                input_voltage = self.dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = self.misc.measure_voltage(1, 'Sourcemeter1')[0]
                vref = self.misc.measure_voltage(2, 'Sourcemeter1')[0]
                voff = self.misc.measure_voltage(1, 'Sourcemeter2')[0]
                vrext = self.misc.measure_voltage(1, 'Sourcemeter3')[0]
                iref = float(self.misc.measure_voltage(2, 'Sourcemeter3')[0])/150000
                
                preliminiary_mirrored_current = float(vrext) / 800
                logging.info("Mirrored current is %r A" % preliminiary_mirrored_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("VDD is %r V" % vdd)
                logging.info("Vref is %r V" % vref)
                logging.info("Voffs is %r V" % voff)
                logging.info("Iref is %r V" % iref)



                self.misc.data.append([iload, input_voltage, vdd, vref, voff, iref, vrext])
                f.writerow(self.misc.data[-1])
                if iin - iload < 2*stepSize:
                    stepSize = 0.001
                iload += stepSize
                if float(iload) > float(max_iload) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")
                
        self.measure_temp()
        self.dut['Sourcemeter1'].set_current(0, channel=1)
        logging.info('Measurement finished.')

        #=======================================================================
        # self.misc.reset(1, 'Sourcemeter1')
        # self.misc.reset(2, 'Sourcemeter1')
        # self.misc.reset(1, 'Sourcemeter2')
        # self.misc.reset(1, 'Sourcemeter3')
        # self.misc.reset(2, 'Sourcemeter3')
        #=======================================================================
    
    def shutdown_tti(self):
        self.dut['VDD1'].set_enable(on=False)
        time.sleep(0.5)
        self.dut['VDD2'].set_enable(on=False)
        
    def working_point(self, load = 0):
        self.dut['Sourcemeter1'].off(channel=1)
        self.dut['Sourcemeter1'].off(channel=2)
        self.dut['Sourcemeter2'].off(channel=1)
        self.dut['Sourcemeter3'].off(channel=1)
        self.dut['Sourcemeter3'].off(channel=2)
        self.shutdown_tti()
        self.misc.reset(1, 'Sourcemeter1')
        self.misc.reset(2, 'Sourcemeter1')
        self.misc.reset(1, 'Sourcemeter2')
        self.misc.reset(1, 'Sourcemeter3')
        self.misc.reset(2, 'Sourcemeter3')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        self.misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        self.misc.set_source_mode('CURR', 2, 'Sourcemeter3')
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        self.dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 1)
        self.dut['Sourcemeter3'].set_voltage_limit(2, channel = 2)
        self.dut['Sourcemeter1'].set_current(load, channel=1)
        self.dut['Sourcemeter1'].set_current(0, channel=2)
        self.dut['Sourcemeter2'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=1)
        self.dut['Sourcemeter3'].set_current(0, channel=2)
        self.dut['Sourcemeter1'].four_wire_on(channel=1)
        self.dut['Sourcemeter1'].four_wire_off(channel=2)
        self.dut['Sourcemeter2'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=1)
        self.dut['Sourcemeter3'].four_wire_off(channel=2)
        self.dut['Sourcemeter1'].on(channel=1)
        self.dut['Sourcemeter1'].on(channel=2)
        self.dut['Sourcemeter2'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=1)
        self.dut['Sourcemeter3'].on(channel=2)
        self.dut['VDD1'].set_current_limit(0.6)
        self.dut['VDD1'].set_voltage(2)
        self.dut['VDD1'].set_enable(on=True)

    def measure_temp(self):
        import math
        temp_log = {}
        self.dut['Sourcemeter4'].set_ohms_measurement()
        ntc = float(self.dut['Sourcemeter4'].get_reading().split(',')[2])
        temp = 1/(1./298.15 + 1./3435. * math.log(ntc/10000.))-273.15
        with open('ntc_log.yaml', 'a') as outfile:
            key = str(time.time())
            temp_log[key] = temp
        logging.info('Current temperature is %f C' % temp)



if __name__ == "__main__":
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)
    iv = IV()
    print(dut['Sourcemeter1'].get_name())
    print(dut['Sourcemeter2'].get_name())
    print(dut['Sourcemeter3'].get_name())
    print(dut['Sourcemeter4'].get_name())
