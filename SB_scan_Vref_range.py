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
    
    def scan_Vref_CURR(self, file_name, Iin, inputPolarity, Iload, loadPolarity, min_Vref, max_Vref, steps, stepSize, Voff):
        '''
        Vref-scan in current supply mode.
        '''
        
        if float(Iin) > float(self.maximumInputCurrent):
            print "ERROR: Iin > maximumInputCurrent"
            return
        if float(Iload) > float(Iin):
            print "ERROR: Iload > Iin"
            return
        
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
        dut['Sourcemeter2'].set_voltage(0.6)    #set Vref
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
            f.writerow(['Reference voltage [V]', 'Input voltage [V]', 'Input current [A]', 'output voltage [V]', 'output-reference ratio [1]'])
            
            
            dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1)                   #set Iin
            dut['Sourcemeter1'].set_current(loadPolarity*Iload, channel=2)                  #set Iload
            
            
            refVolt = min_Vref
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter2'].set_voltage(refVolt)                                    #set Vref
                #
                input_current = Iin#misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                load_current_1 = Iload#misc.measure_current(2, 'Sourcemeter1')[0]           #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]           #measure Vout_1
                reference_voltage_1 = refVolt#misc.measure_voltage(1, 'Sourcemeter2')[0]    #measure Vref_1
                offset_voltage_1 = Voff#misc.measure_voltage(1, 'Sourcemeter3')[0]          #measure Voff_1
                outputRefRatio = output_voltage_1 / reference_voltage_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage_1)
                logging.info("Regulator output-reference voltage ratio is %r" % outputRefRatio)
                #
                #Writing readout in output file
                misc.data.append([refVolt, input_voltage, input_current, output_voltage_1, outputRefRatio])
                f.writerow(misc.data[-1])
                #
                refVolt += stepSize                                                        #Increase input current for next iteration
                if float(refVolt) > float(max_Vref) or float(input_voltage) >= 1.99:       #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        #
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        
        iv.livePlot(file_name)
    
    
    def scan_Vref_VOLT(self, file_name, Vin, inputPolarity, Iload, loadPolarity, min_Vref, max_Vref, steps, stepSize, Voff):
        '''
        Vref-scan in voltage supply mode.
        '''
        
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
        dut['Sourcemeter1'].set_current_range(3, channel = 2)
        #
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #
        dut['Sourcemeter2'].set_voltage(0.6)    #set Vref
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
            f.writerow(['Reference voltage [V]', 'Input voltage [V]', 'Input current [A]', 'output voltage [V]', 'output-reference ratio [1]'])
            
            
            dut['Sourcemeter1'].set_voltage(inputPolarity*Vin, channel=1)                   #set Vin
            dut['Sourcemeter1'].set_current(loadPolarity*Iload, channel=2)                  #set Iload
            
            
            refVolt = min_Vref
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter2'].set_voltage(refVolt)                                    #set Vref
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = Vin#misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                load_current_1 = Iload#misc.measure_current(2, 'Sourcemeter1')[0]           #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]           #measure Vout_1
                reference_voltage_1 = refVolt#misc.measure_voltage(1, 'Sourcemeter2')[0]    #measure Vref_1
                offset_voltage_1 = Voff#misc.measure_voltage(1, 'Sourcemeter3')[0]          #measure Voff_1
                outputRefRatio = output_voltage_1 / reference_voltage_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage_1)
                logging.info("Regulator output-reference voltage ratio is %r" % outputRefRatio)
                #
                #Writing readout in output file
                misc.data.append([refVolt, input_voltage, input_current, output_voltage_1, outputRefRatio])
                f.writerow(misc.data[-1])
                #
                refVolt += stepSize                                                                         #Increase input current for next iteration
                if float(refVolt) > float(max_Vref) or float(input_current) >= self.maximumInputCurrent:    #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        #
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
            if "Reference voltage" in header[i]:
                Vref = i
                logging.info("reference voltage in column %r" % i)
            elif "Input voltage" in header[i]:
                Vin = i
                logging.info("Input voltage in column %r" % i)
            elif "Input current" in header[i]:
                Iin = i
                logging.info("Input current in column %r" % i)
            elif "output voltage" in header[i]:                         #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage in column %r" % i)
        

        V_ref = [None]*len(csvfilearray)
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        V_drop1 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_ref[i] = csvfilearray[i][Vref]
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                V_out1[i] = csvfilearray[i][Vout1]
            except AttributeError:
                pass
            V_drop1[i] = float(V_in[i]) - float(V_out1[i])
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(V_ref, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            #plt.plot(V_ref, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            #plt.axis([0,1.0,1.1,1.4])
            plt.xlabel('Reference Voltage / V')
            plt.ylabel('Output Voltage / V')
        elif "VOLT" in file_name:
            plt.plot(V_ref, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            #plt.axis([0,1.0,1.1,1.4])
            plt.xlabel('Reference Voltage / V')
            plt.ylabel('Output Voltage / V')
        
        plt.legend()
        plt.savefig(file_name+".pdf")



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
    
    
    #
    fileName = "output/Vref_Range_CURR/Vref_Range_CURR_Iin_860mA_Iload_0mA_Voff_800mV.csv"
    
    #iv.scan_Vref_CURR(file_name, Iin,  inputPolarity, Iload, loadPolarity, min_Vref, max_Vref, steps, stepSize, Voff)
    iv.scan_Vref_CURR(fileName,   0.86, 1,             0.0,   -1,           0.45,     0.65,     40,    0.005,     0.8)
    
    
#    #
#    fileName = "output/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1400mV_Iload_0mA_Voff_600mV.csv"
#    
#    #iv.scan_Vref_VOLT(file_name, Vin,  inputPolarity, Iload, loadPolarity, min_Vref, max_Vref, steps, stepSize, Voff)
#    iv.scan_Vref_VOLT(fileName,   1.4,  1,             0.0,   -1,           0.45,     0.65,     40,    0.005,     0.8)
