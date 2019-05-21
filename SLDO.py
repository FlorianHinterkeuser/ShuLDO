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

        misc.reset(1, 'Sourcemeter1')   #Vout
        misc.reset(2, 'Sourcemeter1')   #vref
        misc.reset(1, 'Sourcemeter2')   #Voff
        misc.reset(2, 'Sourcemeter2')   #Vrext
 
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 2, 'Sourcemeter2')     
 
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 2)
 
#        dut['Sourcemeter1'].set_autorange(channel = 1)
#        dut['Sourcemeter1'].set_autorange(channel = 2)
#        dut['Sourcemeter2'].set_autorange(channel = 1)
#        dut['Sourcemeter2'].set_autorange(channel = 2)
#        dut['Sourcemeter3'].set_autorange()
 
        dut['Sourcemeter1'].set_current(0, channel=1)
        dut['Sourcemeter1'].set_current(0, channel=2)
        dut['Sourcemeter2'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0, channel=2)
 
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on(channel=1)
        dut['Sourcemeter2'].on(channel=2)

        fncounter=1
        if OVP_on:
            filename = file_name +"OVP_" + str(OVP_limit)+"V_"+ str(run_number) + ".csv"
        else:
            filename = file_name + "OVP_int_" + str(run_number) + ".csv"
        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Mirrored Current [V]', 'dIin [A]', 'dVin [V]', 'dVDD [V]', 'dVref [V]', 'dVoffs [V]', 'dImirror [V]'])

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
            for x in range(0, int(steps)):
                
                logging.info("Setting Current to %f" % iin)
                dut['VDD1'].set_current_limit(iin)
                time.sleep(0.5)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = misc.measure_voltage(1, 'Sourcemeter1')
                vref = misc.measure_voltage(2, 'Sourcemeter1')
                voff = misc.measure_voltage(2, 'Sourcemeter2')
                vrext = misc.measure_voltage(1, 'Sourcemeter2')
                
                preliminiary_mirrored_current = vrext[0] / 800
                logging.info("Mirrored current is %r A" % preliminiary_mirrored_current)
                logging.info("Digital input voltage is %r V" % input_voltage)
                logging.info("VDD is %r V" % vdd[0])
                logging.info("Vref is %r V" % vref)
                logging.info("Voffs is %r V" % voff)



                misc.data.append([iin, input_voltage, vdd[0], vref[0], voff[0], vrext[0], iin*0.001 , input_voltage*0.001,vdd[1], vref[1], voff[1], vrext[1]])
                f.writerow(misc.data[-1])
                
                iin += stepSize
                if float(iin) > float(max_Iin) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        return iin

    def scan_IV2(self, file_name, max_Iin, inputPolarity, steps, stepSize, run_number=0, remote_sense=True,
                OVP_on=False, OVP_limit=0.5):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")

        misc.reset(1, 'Sourcemeter1')  # Vout
        misc.reset(2, 'Sourcemeter1')  # vref
        misc.reset(1, 'Sourcemeter2')  # Voff
        misc.reset(2, 'Sourcemeter2')  # Vrext

        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 2, 'Sourcemeter2')

        dut['Sourcemeter1'].set_voltage_limit(2, channel=1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel=2)
        dut['Sourcemeter2'].set_voltage_limit(2, channel=1)
        dut['Sourcemeter2'].set_voltage_limit(2, channel=2)

        #        dut['Sourcemeter1'].set_autorange(channel = 1)
        #        dut['Sourcemeter1'].set_autorange(channel = 2)
        #        dut['Sourcemeter2'].set_autorange(channel = 1)
        #        dut['Sourcemeter2'].set_autorange(channel = 2)
        #        dut['Sourcemeter3'].set_autorange()

        dut['Sourcemeter1'].set_current(0, channel=1)
        dut['Sourcemeter1'].set_current(0, channel=2)
        dut['Sourcemeter2'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0, channel=2)

        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on(channel=1)
        dut['Sourcemeter2'].on(channel=2)

        fncounter = 1
        
        if OVP_on:
            filename = file_name +"OVP_" + str(OVP_limit)+"V_"+ str(run_number) + ".csv"
        else:
            filename = file_name + "OVP_int_" + str(run_number) + ".csv"

        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'VDD [V]', 'Vrefpre [V]', 'Voutpre [V]',
                            'Vbandgap [V]', 'dIin [A]', 'dVin [V]', 'dVDD [V]', 'dVrefpre [V]', 'dVoutpre [V]',
                            'dVbandgap [V]'])

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
            for x in range(0, int(steps)):

                logging.info("Setting Current to %f" % iin)
                dut['VDD1'].set_current_limit(iin)
                time.sleep(0.5)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = misc.measure_voltage(1, 'Sourcemeter1')
                vrefpre = misc.measure_voltage(2, 'Sourcemeter1')
                voutpre = misc.measure_voltage(2, 'Sourcemeter2')
                vbandgap = misc.measure_voltage(1, 'Sourcemeter2')

                logging.info("Vbandgap is %r V" % vbandgap)
                logging.info("Digital input voltage is %r V" % input_voltage)
                logging.info("VDD is %r V" % vdd[0])
                logging.info("Vrefpre is %r V" % vrefpre)
                logging.info("Voutpre is %r V" % voutpre)

                misc.data.append([iin, input_voltage, vdd[0], vrefpre[0], voutpre[0], vbandgap[0], iin * 0.001, input_voltage * 0.001, vdd[1], vrefpre[1], voutpre[1], vbandgap[1]])
                f.writerow(misc.data[-1])

                iin += stepSize
                if float(iin) > float(max_Iin) or float(input_voltage) >= 1.999:
                    break
                logging.info("Next step")

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        return iin

    def scan_load_reg(self, file_name, iin, max_iload, steps, stepSize, run_number = 0):
        '''
        IV-scan in current supply mode.
        '''
        logging.info("Starting ...")

        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Imirror
        misc.reset(1, 'Sourcemeter2')   #Vref
        misc.reset(2, 'Sourcemeter2')   #Voffs
        misc.reset(1, 'Multimeter1')
 
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 2, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Multimeter1') 
 
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 2)
        dut['Multimeter1'].set_voltage_limit(2)
 
        dut['Sourcemeter1'].set_current(0, channel=1)
        dut['Sourcemeter1'].set_current(0, channel=2)
        dut['Sourcemeter2'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0, channel=2)
        dut['Multimeter1'].set_current(0)
 
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on(channel=1)
        dut['Sourcemeter2'].on(channel=2)
        dut['Multimeter1'].four_wire_on()
        dut['Multimeter1'].on()

        fncounter=1
        filename = file_name + str(run_number) + ".csv"

        while os.path.isfile(file_name):
            filename = filename.split('.')[0]
            filename = filename + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(filename, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input voltage [V]', 'Load current [A]', 'VDD [V]', 'Vref [V]', 'Voffs [V]', 'Vpre [V]', 'Vbg [V]'])

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
                dut['Multimeter1'].set_current(iload)
                time.sleep(1)

                logging.info("measuring ...")
                input_voltage = dut['VDD1'].get_voltage()
                time.sleep(0.5)
                vdd = misc.measure_voltage(1, 'Multimeter1')[0]
                voffs = misc.measure_voltage(2, 'Sourcemeter1')[0]
                vref = misc.measure_voltage(1, 'Sourcemeter1')[0]
                vpre = misc.measure_voltage(1, 'Sourcemeter2')[0]
                vbg = misc.measure_voltage(2, 'Sourcemeter2')[0]
                
                logging.info("Digital input voltage is %r V" % input_voltage)
                logging.info("Load current is %r A" % iload)
                logging.info("VDD is %r V" % vdd)
                logging.info("Vref is %r V" % vref)
                logging.info("Voffs is %r V" % voffs)
                logging.info("Vpre is %r V" % vpre)
                logging.info("Vbg is %r V" % vbg)



                misc.data.append([input_voltage, iload, vdd, vref, voffs, vpre, vbg])
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
        misc.reset(1, 'Multimeter1')
    
    def shutdown_tti(self):
        dut['VDD1'].set_enable(on=False)
        time.sleep(0.5)
        dut['VDD2'].set_enable(on=False)
        
    def working_point(self):
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(2, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 2, 'Sourcemeter2')
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter2'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter1'].set_current(0, channel=1)
        dut['Sourcemeter1'].set_current(0, channel=2)
        dut['Sourcemeter2'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0, channel=2)
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on(channel=1)
        dut['Sourcemeter2'].on(channel=2)
        dut['VDD2'].set_current_limit(0.6)
        time.sleep(1)
        dut['VDD1'].set_current_limit(0.6)
        inputCurr = 0.001
        dut['VDD2'].set_voltage(0.55)
        time.sleep(0.5)
        dut['VDD1'].set_voltage(2)



if __name__ == "__main__":
    dut = Dut('periphery.yaml')
    dut.init()
    misc = Misc(dut=dut)
    iv = IV()
