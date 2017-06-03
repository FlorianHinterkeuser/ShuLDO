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
    
    def __init__(self):
        """A constructor"""
        self.maximumInputCurrent = 0.0  #for a single regulator
    
    def scan_loadreg_CURR(self, regID1, regID2, dynLoadChipID, file_name, Iin, inputPolarity, max_Iload1, loadPolarity1, steps, stepSize, \
                                                                                                stat_Iload2, loadPolarity2):
        '''
        Load-regulation-scan in current supply mode.
        '''
        
        if float(Iin) > 2*float(self.maximumInputCurrent):
            print "ERROR: Iin > 2*maximumInputCurrent"
            return
        if float(max_Iload1)+float(stat_Iload2) > float(Iin):
            print "ERROR: max_Iload+stat_Iload2 > Iin"
            return
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Iin
        misc.reset(2, 'Sourcemeter1')   #Iload1
        misc.reset(1, 'Sourcemeter2')   #Iload2
        #
        misc.reset(1, 'Sourcemeter3')   #Vshunt1
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('CURR', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        dut['Sourcemeter3'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2)
        dut['Sourcemeter3'].set_voltage_limit(0.05)
        
        #Set source range
        dut['Sourcemeter1'].set_current_range(3, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        dut['Sourcemeter2'].set_current(0)
        #dut['Sourcemeter3'].on()
        dut['Sourcemeter3'].set_current(0)
        
        #Don't overwrite existing .csv-files
        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            #What is written in the output file
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg 1 input current [A]', 'Reg 2 input current [A]', \
                        'Reg 1-'+regID1+' load current [A]', 'Reg 1-'+regID1+' output voltage [V]', \
                        'Reg 2-'+regID2+' load current [A]', 'Reg 2-'+regID2+' output voltage [V]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            
            dut['Sourcemeter1'].set_current(inputPolarity*Iin, channel=1)               #set Iin
            
            
            if dynLoadChipID == '1':
                dut['Sourcemeter2'].set_current(loadPolarity2*stat_Iload2)              #set Iload_stat
            elif dynLoadChipID == '2':
                dut['Sourcemeter1'].set_current(loadPolarity2*stat_Iload2, channel=2)   #set Iload_stat
            
            
            dynLoadCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                if dynLoadChipID == '1':
                    dut['Sourcemeter1'].set_current(loadPolarity1*dynLoadCurr, channel=2)       #set Iload_dyn
                elif dynLoadChipID == '2':
                    dut['Sourcemeter2'].set_current(loadPolarity1*dynLoadCurr)       #set Iload_dyn
                #
                input_current = Iin#misc.measure_current(1, 'Sourcemeter1')[0]              #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                #
                load_current_1 = 0
                load_current_2 = 0
                if dynLoadChipID == '1':
                    load_current_1 = dynLoadCurr*loadPolarity1#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                    load_current_2 = stat_Iload2*loadPolarity2#misc.measure_current(1, 'Sourcemeter2')[0]         #measure Iload_2
                elif dynLoadChipID == '2':
                    load_current_1 = stat_Iload2*loadPolarity2#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                    load_current_2 = dynLoadCurr*loadPolarity1#misc.measure_current(1, 'Sourcemeter2')[0]         #measure Iload_2
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                output_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]       #measure Vout_2
                #
                reference_voltage_1 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_1
                reference_voltage_2 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_2
                outputRefRatio1 = output_voltage_1 / reference_voltage_1
                outputRefRatio2 = output_voltage_2 / reference_voltage_2
                #
                shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter3')[0]        #measure Vshunt_1
                input_current_1 = shunt_voltage_1/Rshunt                            #measure Iin_1
                ##shunt_voltage_2 = misc.measure_voltage(ch..., 'Sourcemeter...')[0]        #measure Vshunt_1
                input_current_2 = input_current - input_current_1                   #measure Iin_2
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1-"+regID1+" load current is %r A" % load_current_1)
                logging.info("Regulator 2-"+regID2+" load current is %r A" % load_current_2)
                logging.info("Regulator 1-"+regID1+" output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 2-"+regID2+" output voltage is %r V" % output_voltage_2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, input_current_2, \
                                  load_current_1*loadPolarity1, output_voltage_1, load_current_2*loadPolarity2, output_voltage_2])
                f.writerow(misc.data[-1])
                #
                dynLoadCurr += stepSize                                                                         #Increase dynamic load current for next iteration
                if float(dynLoadCurr) > float(max_Iload1) or float(input_voltage) >= 1.99 or \
                   -float(dynLoadCurr)*loadPolarity1-float(stat_Iload2)*loadPolarity2 >= float(Iin)*inputPolarity or \
                   float(input_current_1) > float(self.maximumInputCurrent) or float(input_current_2) > float(self.maximumInputCurrent): #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        
        iv.livePlot(file_name, dynLoadChipID)


    def scan_loadreg_VOLT(self, regID1, regID2, dynLoadChipID, file_name, Vin, inputPolarity, max_Iload1, loadPolarity1, steps, stepSize, \
                                                                                                stat_Iload2, loadPolarity2):
        '''
        Load-regulation-scan in voltage supply mode.
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(1, 'Sourcemeter1')   #Vin
        misc.reset(2, 'Sourcemeter1')   #Iload1
        misc.reset(1, 'Sourcemeter2')   #Iload2
        #
        misc.reset(1, 'Sourcemeter3')   #Vshunt1
        
        #Set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 1, 'Sourcemeter1')
        misc.set_source_mode('CURR', 2, 'Sourcemeter1')
        misc.set_source_mode('CURR', 1, 'Sourcemeter2')
        misc.set_source_mode('CURR', 1, 'Sourcemeter3')
        
        #Use 4-wire sensing.
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter1'].four_wire_on(channel=2)         
        dut['Sourcemeter2'].four_wire_on()
        dut['Sourcemeter3'].four_wire_on()
        
        #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(2, channel = 1)
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 2)
        dut['Sourcemeter2'].set_voltage_limit(2)
        dut['Sourcemeter3'].set_voltage_limit(0.05)
        
        #Set source range
        dut['Sourcemeter1'].set_voltage_range(6, channel = 1)
        dut['Sourcemeter1'].set_current_range(1, channel = 2)
        dut['Sourcemeter2'].set_autorange()
        dut['Sourcemeter3'].set_autorange()
        
        #Activate
        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        #dut['Sourcemeter2'].on()
        dut['Sourcemeter2'].set_current(0)
        #dut['Sourcemeter3'].on()
        dut['Sourcemeter3'].set_current(0)
        
        #Don't overwrite existing .csv-files
        fncounter=1
        while os.path.isfile(file_name):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
            #What is written in the output file
            f.writerow(['Input current [A]', 'Input voltage [V]', 'Reg 1 input current [A]', 'Reg 2 input current [A]', \
                        'Reg 1-'+regID1+' load current [A]', 'Reg 1-'+regID1+' output voltage [V]', \
                        'Reg 2-'+regID2+' load current [A]', 'Reg 2-'+regID2+' output voltage [V]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            
            dut['Sourcemeter1'].set_voltage(inputPolarity*Vin, channel=1)               #set Vin
            
            
            if dynLoadChipID == '1':
                dut['Sourcemeter2'].set_current(loadPolarity2*stat_Iload2)              #set Iload_stat
            elif dynLoadChipID == '2':
                dut['Sourcemeter1'].set_current(loadPolarity2*stat_Iload2, channel=2)   #set Iload_stat
            
            
            dynLoadCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                if dynLoadChipID == '1':
                    dut['Sourcemeter1'].set_current(loadPolarity1*dynLoadCurr, channel=2)   #set Iload_dyn
                elif dynLoadChipID == '2':
                    dut['Sourcemeter2'].set_current(loadPolarity1*dynLoadCurr)              #set Iload_dyn
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]                  #measure Iin
                input_voltage = Vin#misc.measure_voltage(1, 'Sourcemeter1')[0]              #measure Vin
                #
                load_current_1 = 0
                load_current_2 = 0
                if dynLoadChipID == '1':
                    load_current_1 = dynLoadCurr*loadPolarity1#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                    load_current_2 = stat_Iload2*loadPolarity2#misc.measure_current(1, 'Sourcemeter2')[0]         #measure Iload_2
                elif dynLoadChipID == '2':
                    load_current_1 = stat_Iload2*loadPolarity2#misc.measure_current(2, 'Sourcemeter1')[0]         #measure Iload_1
                    load_current_2 = dynLoadCurr*loadPolarity1#misc.measure_current(1, 'Sourcemeter2')[0]         #measure Iload_2
                output_voltage_1 = misc.measure_voltage(2, 'Sourcemeter1')[0]       #measure Vout_1
                output_voltage_2 = misc.measure_voltage(1, 'Sourcemeter2')[0]       #measure Vout_2
                #
                reference_voltage_1 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_1
                reference_voltage_2 = 0.6#misc.measure_voltage(ch..., 'Sourcemeter...')[0]    #measure Vref_2
                outputRefRatio1 = output_voltage_1 / reference_voltage_1
                outputRefRatio2 = output_voltage_2 / reference_voltage_2
                #
                shunt_voltage_1 = misc.measure_voltage(1, 'Sourcemeter3')[0]        #measure Vshunt_1
                input_current_1 = shunt_voltage_1/Rshunt                            #measure Iin_1
                ##shunt_voltage_2 = misc.measure_voltage(ch..., 'Sourcemeter...')[0]        #measure Vshunt_1
                input_current_2 = input_current - input_current_1                   #measure Iin_2
                #
                #Logging the readout
                logging.info("Input current is %r A" % input_current)           
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1-"+regID1+" load current is %r A" % load_current_1)
                logging.info("Regulator 2-"+regID2+" load current is %r A" % load_current_2)
                logging.info("Regulator 1-"+regID1+" output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 2-"+regID2+" output voltage is %r V" % output_voltage_2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, input_current_2, \
                                  load_current_1*loadPolarity1, output_voltage_1, load_current_2*loadPolarity2, output_voltage_2])
                f.writerow(misc.data[-1])
                #
                dynLoadCurr += stepSize                                                                         #Increase dynamic load current for next iteration
                if float(dynLoadCurr) > float(max_Iload1) or float(input_current) >= 1.99 or \
                   -float(dynLoadCurr)*loadPolarity1-float(stat_Iload2)*loadPolarity2 >= float(Iin)*inputPolarity or \
                   float(input_current_1) > float(self.maximumInputCurrent) or float(input_current_2) > float(self.maximumInputCurrent): #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        
        iv.livePlot(file_name, dynLoadChipID)


    def livePlot(self, file_name, dynLoadChip_ID):
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
            elif "load current" in header[i] and "Reg 1" in header[i]:
                Iload1 = i
                logging.info("Load current 1 in column %r" % i)
            elif "output voltage" in header[i] and "Reg 1" in header[i]:
                Vout1 = i
                logging.info("Output voltage 1 in column %r" % i)
            elif "load current" in header[i] and "Reg 2" in header[i]:
                Iload2 = i
                logging.info("Load current 2 in column %r" % i)
            elif "output voltage" in header[i] and "Reg 2" in header[i]:
                Vout2 = i
                logging.info("Output voltage 2 in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        I_load1 = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        I_load2 = [None]*len(csvfilearray)
        V_out2 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                I_load1[i] = csvfilearray[i][Iload1]
                V_out1[i] = csvfilearray[i][Vout1]
                I_load2[i] = csvfilearray[i][Iload2]
                V_out2[i] = csvfilearray[i][Vout2]
            except AttributeError:
                pass
        
        
        if "CURR" in file_name or "VOLT" in file_name:
            plt.grid(True)
            if dynLoadChip_ID == '1':
                plt.plot(I_load1, V_in, ".-", markersize=3, linewidth=0.5, color = 'k', label= 'Input Voltage')
                plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Reg 1 Output Voltage')
                plt.plot(I_load1, V_out2, ".-", markersize=3, linewidth=0.5, color = 'g', label = 'Reg 2 Output Voltage')
                plt.xlabel('Reg 1 Load Current / A')
            elif dynLoadChip_ID == '2':
                plt.plot(I_load2, V_in, ".-", markersize=3, linewidth=0.5, color = 'k', label= 'Input Voltage')
                plt.plot(I_load2, V_out1, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Reg 1 Output Voltage')
                plt.plot(I_load2, V_out2, ".-", markersize=3, linewidth=0.5, color = 'r', label = 'Reg 2 Output Voltage')
                plt.xlabel('Reg 2 Load Current / A')
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
    print 'Sourcemeter 3: '+dut['Sourcemeter3'].get_name()
    
    raw_input("Proceed?")
    
    iv = IV()
#    iv.maximumInputCurrent = 1.0    #1A chip
    iv.maximumInputCurrent = 2.0    #2A chip
    
    
    regId_1 = '1'
    regId_2 = '1'
    #
    dynLoad_ChipId = '2'
    
#    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_1000mA_Vref1_600mV_Vref2_500mV_REG1-"+regId_1+"_REG2-"+regId_2+".csv"
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_2000mA_Vref1_600mV_Vref2_500mV_Voff1_1000mV_Voff2_1000mV.csv"
    #iv.livePlot(fileName, dynLoad_ChipId)
    
    #scan_loadreg_CURR(regID1,    regID2,  dynLoadChipID,  file_name, Iin, inputPolarity, max_Iload1, loadPolarity1, steps, stepSize, stat_Iload2, loadPolarity2)
    iv.scan_loadreg_CURR(regId_1, regId_2, dynLoad_ChipId, fileName,  2.0, 1,             1.0,        -1,            50,    0.02,     0.0,         -1)
    
    
#    fileName = "output/Load_Regulation_VOLT/Loadreg_VOLT_Vin_1400mV_Vref1_600mV_Vref2_600mV_REG1-"+regId_1+"_REG2-"+regId_2+".csv"
    
    #scan_loadreg_VOLT(regID1,    regID2,  dynLoadChipID,  file_name, Vin, inputPolarity, max_Iload1, loadPolarity1, steps, stepSize, stat_Iload2, loadPolarity2)
#    iv.scan_loadreg_VOLT(regId_1, regId_2, dynLoad_ChipId, fileName,  1.4, 1,             0.5,        -1,            51,    0.01,     0.0,         -1)
