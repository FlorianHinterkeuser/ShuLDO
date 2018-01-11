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
    def scan_IinVinVout_CURR(self, file_name, max_Iin, inputPolarity, steps, stepSize):
        '''
        IV-scan in current supply mode.
        '''

        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")

        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Iload

        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')       

        dut['Sourcemeter1'].four_wire_on(channel=1)

        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter2'].set_voltage_limit(2)    

        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter2'].set_autorange()

        dut['Sourcemeter1'].set_current(0, channel=1)
        dut['Sourcemeter2'].set_current(0)

        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter2'].on()

        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1

        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Output voltage [V]'])

            inputCurr = 0
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(inputPolarity*inputCurr, channel=1)     #set Iin

                input_current = inputCurr
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]
                output_voltage = misc.measure_voltage(1, 'Sourcemeter2')[0]

                logging.info("Input current is %r A" % input_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage)

                misc.data.append([input_current, input_voltage, output_voltage])
                f.writerow(misc.data[-1])
                
                if inputCurr >= 0.5:
                    stepSize = 0.0001
                inputCurr += stepSize
                if float(inputCurr) > float(max_Iin) or float(input_voltage) >= 1.99:
                    break

        logging.info('Measurement finished.')

        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        iv.livePlot(file_name)

    def livePlot(self, file_name):
        csvfilearray = []
        header = []
        file = []
        
        with open(file_name, 'rb') as csvfile:
            plots = csv.reader(csvfile, delimiter=';')
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
            elif "Output voltage" in header[i]:                         #Beware: lower case "o" in output voltage!
                Vout = i
                logging.info("Output voltage in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        V_out = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = float(csvfilearray[i][Vin])
                I_in[i] = float(csvfilearray[i][Iin])
                V_out[i] = float(csvfilearray[i][Vout])
            except AttributeError:
                pass
        
        
        
        #plt.grid(True)
        plt.plot(I_in, V_out, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
        plt.plot(I_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
        plt.axis("auto")

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

    os.chdir(os.getcwd() + "\output")
    iv = IV()
    fileName = "output/RD53A.csv"
    #iv.scan_IinVinVout_CURR(fileName, 2, 1, 5500, 0.01)
    iv.livePlot("RD53A_Vout.csv")