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
    Class to perform a dual-chip shunt current distribution scan of the FE65 ShuLDO.
    '''
    
    def scan_Ishunt_dist_CURR(self, file_name, max_Iin, inputPolarity, steps, stepSize):
        '''
        IinIshunt-scan in current supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        #misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        #dut['Sourcemeter1'].four_wire_on(channel=2)
        dut['Sourcemeter2'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        #dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(0.010)
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        #dut['Sourcemeter1'].set_current_range(0.001, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        #dut['Sourcemeter1'].on(channel=2)
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
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg 1 shunt current [A]', 'Reg 2 shunt current [A]'])
            
            Rshunt = 0.01    #R02/03 on PCB
            
            inputCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(inputPolarity*inputCurr, channel = 1)   #set Iin
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                ##input_voltage_1 = misc.measure_voltage(1, 'Sourcemeter2')[0]              #measure Vin_1
                ##input_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]              #measure Vin_2
                shunt_current_1 = (1/Rshunt)*misc.measure_voltage(1, 'Sourcemeter2')[0] #measure Ishunt_1
                shunt_current_2 = input_current - shunt_current_1                       #measure Ishunt_2
                #
                ##load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]       #measure Iload_1
                ##load_current_2 = 0#misc.measure_current(2, 'Sourcemeter1')[0]       #measure Iload_2
                #
                #output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]           #measure Vout_1
                #output_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]           #measure Vout_2
                ##reference_voltage_1 = misc.measure_voltage(..., 'Sourcemeter...')[0]    #measure Vref_1
                ##reference_voltage_2 = misc.measure_voltage(..., 'Sourcemeter...')[0]    #measure Vref_2
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1 input current is %r A" % shunt_current_1)
                logging.info("Regulator 2 input current is %r A" % shunt_current_2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, shunt_current_1, shunt_current_2])
                f.writerow(misc.data[-1])
                #
                inputCurr += stepSize                                                                                   #Increase input current for next iteration
                if float(inputCurr) > float(max_Iin) or float(input_voltage) > 1.99 or \
                   float(shunt_current_1) >= 0.90 or float(shunt_current_2) >= 0.90:                                    #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        iv.livePlot(file_name)
    
    
    def scan_Ishunt_dist_VOLT(self, file_name, max_Vin, inputPolarity, steps, stepSize):
        '''
        VinIshunt-scan in voltage supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        #misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        #dut['Sourcemeter1'].four_wire_on(channel=2)
        dut['Sourcemeter2'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(0.02, channel = 1)
        #dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(0.001)
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(6, channel = 1)
        #dut['Sourcemeter1'].set_current_range(0.001, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        #dut['Sourcemeter1'].on(channel=2)
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
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg 1 shunt current [A]', 'Reg 2 shunt current [A]'])
            
            Rshunt = 0.01    #R02/03 on PCB
            #Rshunt_1 = 0.01 #R02 on PCB
            #Rshunt_2 = 0.01 #R03 on PCB
            
            inputVolt = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_voltage(inputPolarity*inputVolt, channel = 1)   #set Vin
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                ##input_voltage_1 = misc.measure_voltage(1, 'Sourcemeter2')[0]              #measure Vin_1
                ##input_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]              #measure Vin_2
                shunt_current_1 = (1/Rshunt)*misc.measure_voltage(1, 'Sourcemeter2')[0] #measure Ishunt_1
                shunt_current_2 = input_current - shunt_current_1                       #measure Ishunt_2
                #
                ##load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]       #measure Iload_1
                ##load_current_2 = 0#misc.measure_current(2, 'Sourcemeter1')[0]       #measure Iload_2
                #
                #output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]           #measure Vout_1
                #output_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]           #measure Vout_2
                ##reference_voltage_1 = misc.measure_voltage(..., 'Sourcemeter...')[0]    #measure Vref_1
                ##reference_voltage_2 = misc.measure_voltage(..., 'Sourcemeter...')[0]    #measure Vref_2
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1 input current is %r A" % shunt_current_1)
                logging.info("Regulator 2 input current is %r A" % shunt_current_2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, shunt_current_1, shunt_current_2])
                f.writerow(misc.data[-1])
                #
                inputVolt += stepSize                                                                                   #Increase input current for next iteration
                if float(inputVolt) > float(max_Vin) or float(input_current) > 0.02:# or \
                    #float(shunt_current_1) >= 0.02 or float(shunt_current_2) >= 0.02:                                    #Maximum values reached?
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
            plots = csv.reader(csvfile, delimiter=',')
            header = next(plots)
            for row in plots:
                csvfilearray.append(row)
        for i in range(0, len(header)):
            if "Input current" in header[i]:
                Iin = i
                logging.info("Input current in column %r" % i)
            if "Input voltage" in header[i]:
                Vin = i
                logging.info("Input voltage in column %r" % i)
            elif "shunt current" in header[i] and "Reg 1" in header[i]:
                Ishunt1 = i
                logging.info("Shunt current 1 in column %r" % i)
            elif "shunt current" in header[i] and "Reg 2" in header[i]:
                Ishunt2 = i
                logging.info("Shunt current 2 in column %r" % i)
        
        
        I_in = [None]*len(csvfilearray)
        V_in = [None]*len(csvfilearray)
        I_shunt1 = [None]*len(csvfilearray)
        I_shunt2 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                I_in[i] = csvfilearray[i][Iin]
                V_in[i] = csvfilearray[i][Vin]
                I_shunt1[i] = csvfilearray[i][Ishunt1]
                I_shunt2[i] = csvfilearray[i][Ishunt2]
            except AttributeError:
                pass
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(I_in, I_shunt1, ".-", markersize=3, linewidth=0.5, label= 'Shunt Current 1')
            plt.plot(I_in, I_shunt2, ".-", markersize=3, linewidth=0.5, label = 'Shunt Current 2')
            plt.xlabel('Total Input Current / A')
            plt.ylabel('Regulator Input Current / A')
        elif "VOLT" in file_name:
            plt.plot(V_in, I_shunt1, ".-", markersize=3, linewidth=0.5, label= 'Shunt Current 1')
            plt.plot(V_in, I_shunt2, ".-", markersize=3, linewidth=0.5, label = 'Shunt Current 2')
            plt.xlabel('Input Voltage / V')
            plt.ylabel('Regulator Input Current / A')
        
        #plt.axis([0,0.9,0,0.5])
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

    regId_1 = '1'
    regId_2 = '1'
    
    fileName = "output/Powerup_ShuntCurrentDist_CURR_Vref1_600mV_Vref2_600mV_REG1-"+regId_1+"_REG2-"+regId_2+".csv"
    
    #scan_Ishunt_dist_CURR(file_name, max_Iin, inputPolarity, steps, stepSize)
    iv.scan_Ishunt_dist_CURR(fileName, 1.4, 1, 70, 0.02)
    
    
#    fileName = "output/Powerup_ShuntCurrent_Distribution_VOLT_Vref1_600mV_Vref2_600mV.csv"
    
    #scan_Ishunt_dist_VOLT(file_name, max_Vin, inputPolarity, steps, stepSize)
#    iv.scan_Ishunt_dist_VOLT(fileName, 1.8, 1, 180, 0.01)
