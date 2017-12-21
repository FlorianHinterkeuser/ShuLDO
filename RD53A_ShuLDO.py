'''
Created on 26.09.2016

@author: Florian
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
    def scan_IinVinVout_CURR(self, file_name, max_Iin, inputPolarity, steps, stepSize, Vref, Voff):
        '''
        IV-scan in current supply mode.
        '''

        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")

        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Iload
        misc.reset(1, 'Sourcemeter2')   #Vref
        misc.reset(1, 'Sourcemeter3')   #Voff

        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('VOLT', 1, 'Sourcemeter2')
        misc.set_source_mode('VOLT', 1, 'Sourcemeter3')        

        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_off(channel=2)

        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_current_limit(0.01)
        dut['Sourcemeter3'].set_current_limit(0.01)        

        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter1'].set_current_range(3, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()

        dut['Sourcemeter2'].set_voltage(Vref)
        dut['Sourcemeter3'].set_voltage(Voff)

        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on()
        dut['Sourcemeter3'].on()

        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Output voltage [V]', 'Reference Voltage [V]', 'Offset Voltage [V]'])

            inputCurr = 0
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(inputPolarity*inputCurr, channel=1)     #set Iin

                input_current = inputCurr
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]
                output_voltage = misc.measure_voltage(2, 'Sourcemeter1')[0]
                reference_voltage = misc.measure_voltage(1, 'Sourcemeter2')[0]
                offset_voltage = misc.measure_voltage(1, 'Sourcemeter3')[0]

                logging.info("Input current is %r A" % input_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage)
                logging.info("Regulator reference voltage ratio is %r" % reference_voltage)
                logging.info("Regulator offset voltage ratio is %r" % offset_voltage)

                misc.data.append([input_current, input_voltage, output_voltage, reference_voltage, offset_voltage])
                f.writerow(misc.data[-1])

                inputCurr += stepSize
                if float(inputCurr) > float(max_Iin) or float(input_voltage) >= 1.99:
                    break

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        iv.livePlot(file_name)

    def livePlot(self, file_name):
        csvfilearray = []
        header = []
        file = []
        
        with open(file_name, 'rb') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            header = next(plots)
            for row in plots:
                csvfilearray.append(row)
        for i in range(0, len(header)):
            if "Input voltage" in header[i]:
                Vin = i
                logging.info("Input voltage in column %r" % i)
            elif "Input current" in header[i]:
                Iin = i
                logging.info("Input current in column %r" % i)
            elif "output voltage" in header[i]:                         #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        V_drop1 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                V_out1[i] = csvfilearray[i][Vout1]
            except AttributeError:
                pass
            V_drop1[i] = float(V_in[i]) - float(V_out1[i])
        
        
        plt.grid(True)
        
        plt.plot(I_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
        plt.plot(I_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
        plt.axis([0,2.0,0,2.0])
        plt.xlabel('Input Current / A')
        plt.ylabel('Voltage / V')
        
        plt.legend()
        plt.savefig(file_name+".pdf")



if __name__ == '__main__':

    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)

    print 'Sourcemeter 1: '+dut['Sourcemeter1'].get_name()
    print 'Sourcemeter 2: '+dut['Sourcemeter2'].get_name()


    iv = IV()
    fileName = "output/IV_CURR/IV_CURR_Vref_600mV_Voff_800mV.csv"