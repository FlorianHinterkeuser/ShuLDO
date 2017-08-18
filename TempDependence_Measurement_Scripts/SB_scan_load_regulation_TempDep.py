'''
Created on 24.05.2017

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
    
    def scan_loadreg_CURR(self, file_name, Iin, inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff):
        '''
        Load-regulation-scan in current supply mode.
        '''
        
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
        dut['Sourcemeter1'].set_current_range(3, channel = 2)
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
        
        
        #Don't overwrite existing .csv-files
        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            #What is written in the output file
            f.writerow(['load current [A]', 'Input voltage [V]', 'output voltage [V]', 'output-reference ratio [1]', 'Temp-Sensor 1', 'Temp-Sensor 2'])
            
            
            dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1)               #set Iin
            
            temperature_1 = 500
            temperature_2 = 500
            
            loadCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(loadPolarity*loadCurr, channel=2)       #set Iload
                #
                input_current = Iin#misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                load_current_1 = loadCurr#misc.measure_current(2, 'Sourcemeter1')[0]        #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]           #measure Vout_1
                reference_voltage_1 = Vref#misc.measure_voltage(1, 'Sourcemeter2')[0]       #measure Vref_1
                offset_voltage_1 = Voffs#misc.measure_voltage(1, 'Sourcemeter3')[0]         #measure Voff_1
                outputRefRatio = output_voltage_1 / reference_voltage_1
                #
                if loadCurr == 0 or float(loadCurr)+2*float(stepSize) > float(max_Iload):
                    tStr = dutTemp['Thermohygrometer'].get_temperature()
                    temperature_1 = tStr[0]
                    temperature_2 = tStr[1]
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage_1)
                logging.info("Regulator output-reference voltage ratio is %r" % outputRefRatio)
                logging.info("Ambient Temperature 1 is %r" % temperature_1)
                logging.info("Ambient Temperature 2 is %r" % temperature_2)
                #
                #Writing readout in output file
                misc.data.append([load_current_1, input_voltage, output_voltage_1, outputRefRatio, temperature_1, temperature_2])
                f.writerow(misc.data[-1])
                #
                loadCurr += stepSize                                                        #Increase input current for next iteration
                if float(loadCurr) > float(max_Iload) or float(input_voltage) >= 1.99:      #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        #misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        #
        #misc.reset(1, 'Sourcemeter2')
        #misc.reset(1, 'Sourcemeter3')
        dut['Sourcemeter1'].set_current(inputPolarity*1.0, channel=1)       #set Iin
        
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
            elif "load current" in header[i]:
                Iload1 = i
                logging.info("load current in column %r" % i)
            elif "output voltage" in header[i]:                         #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_load1 = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        V_drop1 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_load1[i] = csvfilearray[i][Iload1]
                V_out1[i] = csvfilearray[i][Vout1]
            except AttributeError:
                pass
            V_drop1[i] = float(V_in[i]) - float(V_out1[i])
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            plt.plot(I_load1, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            #plt.axis([0,1.0,1.1,1.4])
            plt.xlabel('Load Current / A')
            plt.ylabel('Voltage / V')
        
        plt.legend()
        plt.savefig("output/Load_Regulation_CURR/manyPlots/"+file_name.split("output/Load_Regulation_CURR/")[1]+".pdf")



if __name__ == '__main__':
    
    #Calling scan_misc with dut = Dut('devices.yaml')
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)
    
    dutTemp = Dut('sensirionEKH4.yaml')
    dutTemp.init()
    print dutTemp['Thermohygrometer'].get_temperature()
    
    #Get meter ID to check communication
    print 'Sourcemeter 1: '+dut['Sourcemeter1'].get_name()
    print 'Sourcemeter 2: '+dut['Sourcemeter2'].get_name()
    print 'Sourcemeter 3: '+dut['Sourcemeter3'].get_name()
    
    raw_input("Proceed?")
    
    iv = IV()
    
    
    temperature = "-30"       #ambient temperature / degree celsius
    
    
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_860mA_Vref_500mV_Voffs_800mV_Temp_"+temperature+"C.csv"
    
    #scan_loadreg_CURR(file_name,  Iin,  inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff)
    iv.scan_loadreg_CURR(fileName, 0.86, 1,             0.86,      -1,           100,   0.01,     0.5,  0.8)
    
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_1130mA_Vref_600mV_Voffs_600mV_Temp_"+temperature+"C.csv"
    
    #scan_loadreg_CURR(file_name,  Iin,  inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff)
    iv.scan_loadreg_CURR(fileName, 1.13, 1,             1.00,      -1,           100,   0.01,     0.6,  0.6)
    
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_860mA_Vref_600mV_Voffs_800mV_Temp_"+temperature+"C.csv"
    
    #scan_loadreg_CURR(file_name,  Iin,  inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff)
    iv.scan_loadreg_CURR(fileName, 0.86, 1,             0.86,      -1,           100,   0.01,     0.6,  0.8)
    
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_1000mA_Vref_600mV_Voffs_1000mV_Temp_"+temperature+"C.csv"
    
    #scan_loadreg_CURR(file_name,  Iin,  inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff)
    iv.scan_loadreg_CURR(fileName, 1.00, 1,             1.00,      -1,           100,   0.01,     0.6,  1.0)
    
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_1000mA_Vref_600mV_Voffs_1200mV_Temp_"+temperature+"C.csv"
    
    #scan_loadreg_CURR(file_name,  Iin,  inputPolarity, max_Iload, loadPolarity, steps, stepSize, Vref, Voff)
    iv.scan_loadreg_CURR(fileName, 1.00, 1,             1.00,      -1,           100,   0.01,     0.6,  1.2)
