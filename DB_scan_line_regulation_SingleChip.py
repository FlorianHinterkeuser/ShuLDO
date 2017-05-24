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
    
    def scan_IinVinVout_CURR(self, chipID, regID, file_name, max_Iin, inputPolarity, steps, stepSize):
        '''
        IV-scan in current supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #IloadN-M
        misc.reset(1, 'Sourcemeter2')   #VshuntN
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(0.01)
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(1, channel = 1)
        dut['Sourcemeter1'].set_current_range(0.001, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        dut['Sourcemeter2'].set_current(0)
        
        #Don't overwrite existing .csv-files
        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            #What is written in the output file
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg '+chipID+'-'+regID+' output voltage [V]', \
                        'Reg '+chipID+'-'+regID+' output-reference ratio [1]', 'Reg '+chipID+' shunt voltage [V]', 'Reg '+chipID+' input current [A]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            inputCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(inputPolarity*inputCurr, channel=1) #set Iin
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]          #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]          #measure Vin
                load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                reference_voltage_1 = 0.6#misc.measure_voltage(1, 'Sourcemeter2')[0]    #measure Vref_1
                outputRefRatio = output_voltage_1 / reference_voltage_1
                shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter2')[0]        #measure Vshunt_1
                input_current_1 = shunt_voltage_1/Rshunt                            #measure Iin_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage_1)
                logging.info("Regulator output-reference voltage ratio is %r" % outputRefRatio)
                logging.info("Regulator shunt voltage is %r V" % shunt_voltage_1)
                logging.info("Regulator input current is %r A" % input_current_1)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, output_voltage_1, outputRefRatio, shunt_voltage_1, input_current_1])
                f.writerow(misc.data[-1])
                #
                inputCurr += stepSize                                                                                   #Increase input current for next iteration
                if float(inputCurr) > float(max_Iin) or float(input_voltage) >= 1.99 or float(input_current_1) >= 0.99: #Maximum values reached?
                    break
                ##if (float(inputCurr) >= 0.3 and float(inputCurr) < 0.3+stepSize) or \
                ##   (float(inputCurr) >= 0.6 and float(inputCurr) < 0.6+stepSize):
                ##    raw_input("Write down second shunt voltage? (Iin = "+str(input_current)+")")
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        iv.livePlot(file_name)
    
    
    def scan_IinVinVout_VOLT(self, chipID, regID, file_name, max_Vin, inputPolarity, steps, stepSize):
        '''
        IV-scan in voltage supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        #misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        #misc.set_source_mode('VOLT', 1, 'Sourcemeter2')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        #dut['Sourcemeter2'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(0.05, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        #dut['Sourcemeter2'].set_voltage_limit(2)
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(2, channel = 1)
        dut['Sourcemeter1'].set_current_range(0.001, channel = 2)
        #dut['Sourcemeter2'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        #dut['Sourcemeter2'].set_current(0)
        
        #Don't overwrite existing .csv-files
        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            #What is written in the output file
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg '+chipID+'-'+regID+' output voltage [V]', \
                        'Reg '+chipID+'-'+regID+' output-reference ratio [1]', 'Reg '+chipID+' shunt voltage [V]', 'Reg '+chipID+' input current [A]'])
            
            Rshunt_1 = 0.01 #R02 on PCB
            Rshunt_2 = 0.01 #R03 on PCB
            
            inputVolt = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_voltage(inputPolarity*inputVolt, channel=1) #set Vin
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]          #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]          #measure Vin
                load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                reference_voltage_1 = 0.6#misc.measure_voltage(1, 'Sourcemeter2')[0]    #measure Vref_1
                outputRefRatio = output_voltage_1 / reference_voltage_1
                #shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter2')[0]        #measure Vshunt_1
                #input_current_1 = shunt_voltage_1/Rshunt_1                          #measure Iin_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator output voltage is %r V" % output_voltage_1)
                logging.info("Regulator output-reference voltage ratio is %r" % outputRefRatio)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, output_voltage_1, outputRefRatio])
                f.writerow(misc.data[-1])
                #
                inputVolt += stepSize                                                                               #Increase input current for next iteration
                if float(inputVolt) > float(max_Vin) or float(input_current) >= 0.05:                               #Maximum values reached?
                    break
                ##if (float(inputCurr) >= 0.3 and float(inputCurr) < 0.3+stepSize) or \
                ##   (float(inputCurr) >= 0.6 and float(inputCurr) < 0.6+stepSize):
                ##    raw_input("Write down second shunt voltage? (Iin = "+str(input_current)+")")
        
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
            elif "input current" in header[i] and "Reg" in header[i]:
                Iin1 = i
                logging.info("Regulator input current in column %r" % i)
            elif "output voltage" in header[i] and "Reg" in header[i]:                    #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage in column %r" % i)
            elif "shunt voltage" in header[i] and "Reg" in header[i]:
                Vshunt1 = i
                logging.info("Shunt voltage in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        I_in1 = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        V_drop1 = [None]*len(csvfilearray)
        V_shunt1 = [None]*len(csvfilearray)
        
        
        if "CURR" in file_name:
            for i in range(0, len(csvfilearray)):
                try:
                    V_in[i] = float(csvfilearray[i][Vin]) - float(csvfilearray[i][Vshunt1])
                    I_in[i] = csvfilearray[i][Iin]
                    I_in1[i] = csvfilearray[i][Iin1]
                    V_out1[i] = csvfilearray[i][Vout1]
                    V_shunt1[i] = csvfilearray[i][Vshunt1]
                except AttributeError:
                    pass
                V_drop1[i] = float(V_in[i]) - float(V_out1[i])
        elif "VOLT" in file_name:
            for i in range(0, len(csvfilearray)):
                try:
                    V_in[i] = csvfilearray[i][Vin]
                    I_in[i] = csvfilearray[i][Iin]
                    V_out1[i] = csvfilearray[i][Vout1]
                except AttributeError:
                    pass
                V_drop1[i] = float(V_in[i]) - float(V_out1[i])

        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(I_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            plt.plot(I_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            #plt.plot(I_in, V_drop1, ".-", markersize=3, linewidth=0.5, color = 'g', label = 'Dropout Voltage')
            #plt.plot(I_in, V_shunt1, ".-", markersize=3, linewidth=0.5, color = 'y', label = 'Shunt Voltage')
            plt.axis([0,0.9,0,2.0])
            plt.xlabel('Input Current / A')
            plt.ylabel('Voltage / V')
        elif "VOLT" in file_name:
            plt.plot(V_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            plt.plot(V_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            #plt.plot(V_in, V_drop1, ".-", markersize=3, linewidth=0.5, color = 'g', label = 'Dropout Voltage')
            plt.plot(V_in, I_in, ".-", markersize=3, linewidth=0.5, color = 'y', label = 'Input Current')
            plt.xlabel('Input Voltage / V')
            plt.ylabel('Voltage / V; Current / A')
            plt.axis([0,1.9,0,2.0])
        
        plt.legend()
        plt.savefig(file_name + '.pdf')



if __name__ == '__main__':
    
    #Calling scan_misc with dut = Dut('devices.yaml')
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)
    
    #Get meter ID to check communication
    print 'Sourcemeter 1: '+dut['Sourcemeter1'].get_name()
    print 'Sourcemeter 2: '+dut['Sourcemeter2'].get_name()
    
    raw_input("Proceed?")
    
    iv = IV()
    
    chipId = '2'
    regId = '1'
    
    fileName = "output/IV_CURR_Iload_0mA_Vref_600mV_REG"+chipId+"-"+regId+".csv"
    
    #scan_IinVinVout_CURR(chipID, regID, file_name, max_Iin, inputPolarity, steps, stepSize)
    iv.scan_IinVinVout_CURR(chipId, regId, fileName, 0.75, 1, 140, 0.005)
    
#    fileName = "output/IV_VOLT_Iload_0mA_Vref_600mV_REG"+chipId+"-"+regId+".csv"

    #scan_IinVinVout_VOLT(chipID, regID, file_name, max_Vin, inputPolarity, steps, stepSize)
#    iv.scan_IinVinVout_VOLT(chipId, regId, fileName, 1.8, 1, 72, 0.025)
