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
    
    def scan_loadreg_CURR(self, chipID, regID, file_name, Iin, inputPolarity, max_Iload, loadPolarity, steps, stepSize):
        '''
        Load-regulation-scan in current supply mode.
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
        dut['Sourcemeter2'].set_voltage_limit(0.02)
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
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
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg '+chipID+"-"+regID+' input current [A]', \
                        'Reg '+chipID+"-"+regID+' load current [A]', 'Reg '+chipID+"-"+regID+' output voltage [V]', \
                        'Reg '+chipID+"-"+regID+' output-reference ratio [1]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            
            dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1)               #set Iin
            
            
            loadCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(loadPolarity*loadCurr, channel=2)   #set Iload
                #
                input_current = Iin#misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                #
                load_current_1 = loadCurr*loadPolarity#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                #
                reference_voltage_1 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_1
                outputRefRatio1 = output_voltage_1 / reference_voltage_1
                #
                shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter3')[0]        #measure Vshunt_1
                input_current_1 = shunt_voltage_1/Rshunt                            #measure Iin_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator "+chipID+"-"+regID+" load current is %r A" % load_current_1)
                logging.info("Regulator "+chipID+"-"+regID+" output voltage is %r V" % output_voltage_1)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, load_current_1*loadPolarity, output_voltage_1, outputRefRatio1])
                f.writerow(misc.data[-1])
                #
                loadCurr += stepSize                                                        #Increase dynamic load current for next iteration
                if float(loadCurr) > float(max_Iload) or float(input_voltage) >= 1.99 or \
                   -float(loadCurr)*loadPolarity >= float(Iin)*inputPolarity:               #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        
        iv.livePlot(file_name)


    def scan_loadreg_VOLT(self, chipID, regID, file_name, Vin, inputPolarity, max_Iload, loadPolarity, steps, stepSize):
        '''
        Load-regulation-scan in voltage supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Vin
        misc.reset(2, 'Sourcemeter1')   #IloadN-M
        misc.reset(1, 'Sourcemeter2')   #VshuntN
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(1, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(0.02)
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(6, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
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
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg '+chipID+"-"+regID+' input current [A]', \
                        'Reg '+chipID+"-"+regID+' load current [A]', 'Reg '+chipID+"-"+regID+' output voltage [V]', \
                        'Reg '+chipID+"-"+regID+' output-reference ratio [1]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            
            dut['Sourcemeter1'].set_voltage(inputPolarity*Vin, channel=1)               #set Vin
            
            
            loadCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(loadPolarity*loadCurr, channel=2)   #set Iload
                #
                input_current = Iin#misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                #
                load_current_1 = loadCurr*loadPolarity#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                #
                reference_voltage_1 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_1
                outputRefRatio1 = output_voltage_1 / reference_voltage_1
                #
                shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter3')[0]        #measure Vshunt_1
                input_current_1 = shunt_voltage_1/Rshunt                            #measure Iin_1
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator "+chipID+"-"+regID+" load current is %r A" % load_current_1)
                logging.info("Regulator "+chipID+"-"+regID+" output voltage is %r V" % output_voltage_1)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, load_current_1*loadPolarity, output_voltage_1, outputRefRatio1])
                f.writerow(misc.data[-1])
                #
                loadCurr += stepSize                                                        #Increase dynamic load current for next iteration
                if float(loadCurr) > float(max_Iload) or float(input_current) >= 0.99 or \
                   -float(loadCurr)*loadPolarity >= float(Iin)*inputPolarity:               #Maximum values reached?
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
            if "Input voltage" in header[i]:
                Vin = i
                logging.info("Input voltage in column %r" % i)
            elif "Input current" in header[i]:
                Iin = i
                logging.info("Input current in column %r" % i)
            elif "load current" in header[i] and "Reg" in header[i]:
                Iload1 = i
                logging.info("Load current in column %r" % i)
            elif "output voltage" in header[i] and "Reg" in header[i]:
                Vout1 = i
                logging.info("Output voltage in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        I_load1 = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                I_load1[i] = csvfilearray[i][Iload1]
                V_out1[i] = csvfilearray[i][Vout1]
            except AttributeError:
                pass
        
        
        if "CURR" in file_name:
            plt.grid(True)
            plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            plt.xlabel('Load Current / A')
            plt.ylabel('Output Voltage / V')
            #plt.axis([0,0.5,1.1,1.5])
            plt.legend()
            plt.savefig(file_name + '.pdf')
        if "VOLT" in file_name:
            plt.grid(True)
            plt.plot(I_load1, V_in, ".-", markersize=3, linewidth=0.5, color = 'k', label= 'Input Voltage')
            plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            plt.xlabel('Load Current / A')
            plt.ylabel('Voltage / V')
            #plt.axis([0,0.5,1.1,1.5])
            plt.legend()
            plt.savefig(file_name + '.pdf')
        else:
            print "Data not found"



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
    
    
    chipId = '1'
    regId  = '1'
    
    fileName = "output/Loadreg_CURR_Iin_1000mA_Vref1_600mV_Vref2_600mV_REG1-"+regId_1+"_REG2-"+regId_2+".csv"
        
    #iv.scan_loadreg_CURR(chipID, regID, file_name, Iin, inputPolarity, max_Iload, loadPolarity, steps, stepSize)
    iv.scan_loadreg_CURR(chipId,  regId, fileName,  0.5, 1,             0.5,       -1,            51,   0.01)
    
    
    
#    fileName = "output/Loadreg_VOLT_Iin_1000mA_Vref1_600mV_Vref2_600mV_REG1-"+regId_1+"_REG2-"+regId_2+".csv"
#        
#    #iv.scan_loadreg_VOLT(chipID, regID, file_name, Vin, inputPolarity, max_Iload, loadPolarity, steps, stepSize)
#    iv.scan_loadreg_VOLT(chipId,  regId, fileName,  1.4, 1,             0.5,       -1,            51,   0.01)
