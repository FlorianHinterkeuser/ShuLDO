'''
Created on 26.09.2016

@author: Florian
'''
import logging
import csv
import os.path
import time
import numpy as np
import math


from scan_misc import Misc
from basil.dut import Dut

dut = Dut('periphery.yaml')
dut.init()
misc = Misc(dut=dut)
class IV(object):
    
    '''
    Class to perform a standard IV scan of the RD53A ShuLDO.
    '''
    
    def scan_init(self, remote_sense, sourcemeter, multimeter):
        
        for smu in sourcemeter:
            misc.reset(1, smu)
            misc.set_source_mode('CURR', 1, smu)
            try:
                misc.reset(2, smu)
                misc.set_source_mode('CURR', 2, smu)
            except: pass
            if '2602A' in misc.get_device_type(smu):
                if remote_sense == True:
                    dut[smu].four_wire_on(channel=1)
                    dut[smu].four_wire_on(channel=2)
                elif remote_sense == False:
                    dut[smu].four_wire_off(channel=1)
                    dut[smu].four_wire_off(channel=2)
                else: raise RuntimeError           
                dut[smu].set_voltage_limit(2, channel = 1)
                dut[smu].set_voltage_limit(2, channel = 2)
                dut[smu].set_current_range(3, channel = 1)
                dut[smu].set_current_range(3, channel = 2)
                dut[smu].set_current(0, channel=1)
                dut[smu].set_current(0, channel=2)
                dut[smu].on(channel=1)
                dut[smu].on(channel=2)
            else:
#                dut[smu].four_wire_on()
                dut[smu].set_voltage_limit(2)
                dut[smu].set_autorange()
                dut[smu].set_current(0)
                dut[smu].on()
    
    def scan_IV(self, file_name, max_Iin, inputPolarity, steps, stepSize, run_number = 0, remote_sense = True, OVP_on = False, OVP_limit = 0.5):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")

        misc.set_scan('Sourcemeter1', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter1', channel=2, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter2', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter2', channel=2, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter3', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter3', channel=2, mode='VOLT', vlim=0.5, ilim=1.5)

        fncounter=1

        if OVP_on:
            filename = str(run_number) + '_' + file_name + "OVP_" + str(OVP_limit)+"V_"+ "_LineReg.csv"
        else:
            filename =  str(run_number) + "_"+ file_name + "_LineReg.csv"
        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1


        if os.path.isfile(filename):
            logging.error("Change run number, you moron!")
            raise RuntimeError

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Iref [V]', 'Vbg [V]', 'NTC [Ohm]', 'dIin [A]', 'dVin [V]', 'dVDD [V]', 'dVref [V]', 'dVoffs [V]', 'dIref [V]', 'dVbg [V]', 'dNTC [Ohm]'])

            dut['VDD1'].set_current_limit(0)
            time.sleep(1)
            iin = 0.001
            dut['VDD1'].set_voltage(2)
            time.sleep(0.5)
            dut['VDD1'].reset_trip()
            time.sleep(0.5)
            if OVP_on:
                dut['VDD2'].set_voltage(OVP_limit)
                time.sleep(0.5)
                dut['VDD2'].set_enable(on=True)
            dut['VDD1'].set_enable(on=True)
            time.sleep(1)
            dut["Sourcemeter1"].four_wire_on(channel=1)
            for x in range(0, int(steps)):
                
                logging.info("Setting Current to %f" % iin)
                dut['VDD1'].set_current_limit(iin)
                time.sleep(0.5)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
#                time.sleep(0.5)
                vdd = misc.measure_voltage(1, 'Sourcemeter1')
                vref = misc.measure_voltage(2, 'Sourcemeter1')
                voff = misc.measure_voltage(2, 'Sourcemeter2')
                iref = misc.measure_voltage(1, 'Sourcemeter2')
                voutpre = misc.measure_voltage(1, 'Sourcemeter3')
                #vext = misc.measure_voltage(0, 'Multimeter2')
                ntc = misc.measure_resistance(2, 'Sourcemeter3')
#                preliminiary_mirrored_current = vrext[0] / 800
#                logging.info("Mirrored current is %f Ohm" % ntc)
#                logging.info("Digital input voltage is %r V" % input_voltage)
#                logging.info("VDD is %r V" % vdd[0])
#                logging.info("Vref is %r V" % vref)
#                logging.info("Voffs is %r V" % voff)



                misc.data.append([iin, input_voltage, vdd[0], vref[0], voff[0], iref[0], voutpre[0], ntc[0], iin*0.002+0.005 , input_voltage*0.001+0.01,vdd[1], vref[1], voff[1], iref[1], voutpre[1], ntc[1]])
                f.writerow(misc.data[-1])
                
                iin += stepSize
                if float(iin) > float(max_Iin) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        misc.reset(2, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter3')
        return iin

    def scan_load_reg(self, file_name, iin, max_iload, steps, stepSize, run_number = 0):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")

        misc.set_scan(device='Sourcemeter1', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan(device='Sourcemeter1', channel=2, mode='CURR', vlim=2, ilim=0)
        misc.set_scan(device='Sourcemeter2', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan(device='Sourcemeter2', channel=2, mode='CURR', vlim=2, ilim=0)
        misc.set_scan(device='Sourcemeter3', channel=1, mode='CURR', vlim=2, ilim=0)
        misc.set_scan(device='Sourcemeter3', channel=2, mode='VOLT', vlim=0.5, ilim=1.5)

        misc.set_source_mode('CURR', 1, 'Sourcemeter1') 

        dut["Sourcemeter1"].four_wire_on(channel=1)
        fncounter=1
        filename = str(run_number) + "_"+ file_name + "_LoadReg.csv"

        if os.path.isfile(filename):
            logging.error("Change run number, you moron!")
            raise RuntimeError

        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + "LoadReg.csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Load current [A]', 'Input voltage [V]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Vpre [V]', 'Vbg [V]', 'NTC [Ohm]', 'dVin [V]', 'dIload [A]', 'dVDD [V]', 'dVref [V]', 'dVoffs [V]', 'dVpre [V]', 'dVbg [V]', 'dNTC [Ohm]'])

            dut['VDD1'].set_current_limit(iin)
            time.sleep(1)
            iload = 0
            dut['VDD1'].set_voltage(1.99)
            time.sleep(0.5)
            dut['VDD1'].reset_trip()
            time.sleep(0.5)
            dut['VDD1'].set_enable(on=True)
            time.sleep(1)
            for x in range(0, int(steps)):
                
                logging.info("Setting Current")
                dut['Sourcemeter1'].set_current(iload, channel = 1)
                time.sleep(1)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = misc.measure_voltage(1, 'Sourcemeter1')
                voffs = misc.measure_voltage(2, 'Sourcemeter2')
                vref = misc.measure_voltage(2, 'Sourcemeter1')
                iref = misc.measure_voltage(1, 'Sourcemeter2')
                voutpre = misc.measure_voltage(1, 'Sourcemeter3')
                ntc = misc.measure_resistance(2, 'Sourcemeter3')


                misc.data.append([iload, input_voltage, vdd[0], vref[0], voffs[0], iref[0], voutpre[0], ntc[0], iload*0.002+0.005, input_voltage*0.001+0.01, vdd[1], vref[1], voffs[1], iref[1], voutpre[1], ntc[1]])
                f.writerow(misc.data[-1])
                if iin - iload < 2*stepSize:
                    stepSize = 0.001
                iload += stepSize
                if float(iload) > float(max_iload) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        misc.reset(2, 'Sourcemeter3')

    def current_mirror(self, file_name, max_Iin, inputPolarity, steps, stepSize, run_number = 0):
        '''
            Different methodes to estimate k-value
        '''
        logging.info("Starting ...")

        misc.set_scan('Sourcemeter2', channel=2, mode='CURR', vlim=2, ilim=0)
        misc.set_scan('Sourcemeter2', channel=1, mode='VOLT', vlim=0, ilim=0.1)
        misc.set_scan(device='Sourcemeter3', channel=2, mode='VOLT', vlim=0.5, ilim=1.5)

        fncounter = 1

        filename = str(run_number) + "_" + file_name + ".csv"
        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        if os.path.isfile(filename):
            logging.error("Change run number, you moron!")
            raise RuntimeError

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(
                ['Input current [A]', 'Input voltage [V]', 'Vext [V]', 'Iext [A]', 'NTC [Ohm]', 'dIin [A]', 'dVin [V]', 'dVext [V]', 'dIext [A]', 'dNTC [Ohm]'])

            dut['VDD1'].set_current_limit(0)
            time.sleep(1)
            iin = 0.001
            dut['VDD1'].set_voltage(2)
            time.sleep(0.5)
            dut['VDD1'].reset_trip()
            time.sleep(0.5)

            dut['VDD1'].set_enable(on=True)
            time.sleep(1)

            for x in range(0, int(steps)):

                logging.info("Setting Current to %f" % iin)
                dut['VDD1'].set_current_limit(iin)
                time.sleep(0.5)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
                #time.sleep(1)
                vext = misc.measure_voltage(2, 'Sourcemeter2')
                iext = misc.measure_current(1, 'Sourcemeter2')
                #iext = [0, 0]
                ntc = misc.measure_resistance(2, 'Sourcemeter3')

                misc.data.append(
                    [iin, input_voltage, vext[0], iext[0], ntc[0], iin * 0.002 + 0.005,
                     input_voltage * 0.001 + 0.01, vext[1], iext[1], ntc[1]])
                f.writerow(misc.data[-1])

                iin += stepSize
                if float(iin) > float(max_Iin) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter3')

        return iin

    def shutdown_tti(self):
        dut['VDD1'].set_enable(on=False)

        time.sleep(0.5)
        #dut['VDD2'].set_enable(on=False)
        
    def working_point(self):
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        misc.reset(2, 'Sourcemeter3')
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 2, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        misc.set_source_mode('VOLT', 2, 'Sourcemeter3')
        dut["Sourcemeter1"].four_wire_on(channel=1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter3'].set_voltage_limit(2, channel=1)
        dut['Sourcemeter3'].set_voltage(0.5, channel=2)
        dut['Sourcemeter1'].set_current(0.5, channel=1)
        dut['Sourcemeter1'].set_current(0, channel=2)
        dut['Sourcemeter2'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0, channel=2)
        dut['Sourcemeter3'].set_current(0, channel=1)
        dut['Sourcemeter3'].set_current_limit(1.5, channel=2)
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on(channel=1)
        dut['Sourcemeter2'].on(channel=2)
        dut['Sourcemeter3'].on(channel=1)
        dut['Sourcemeter3'].on(channel=2)
        #dut['VDD2'].set_current_limit(0.6)
        time.sleep(1)
        dut['VDD1'].set_current_limit(0.6)
        #dut['VDD2'].set_voltage(0.55)
        time.sleep(0.5)
        dut['VDD1'].set_voltage(2)
        time.sleep(0.5)
        dut['VDD1'].reset_trip()
        dut['VDD1'].set_enable(on=True)



def temp_check():
    ntc = np.empty(10)
    for i in range(10):
        ntc[i] = misc.measure_resistance(2, 'Sourcemeter3')[0]
        ntc[i] = 1/(1./298.15 + 1./3435. * math.log(ntc[i]/10000.))-273.15
        time.sleep(0.5)
    ntc_mean = np.mean(ntc)
    ntc_std = np.std(ntc)
    print(ntc[0])
    print(ntc[-1])
    print(ntc_mean)
    print(ntc_std)



if __name__ == "__main__":
    dut = Dut('periphery.yaml')
    dut.init()
    misc = Misc(dut=dut)
    print(dut["Sourcemeter1"].get_name())
    print(dut["Sourcemeter2"].get_name())
    print(dut["Sourcemeter3"].get_name())

