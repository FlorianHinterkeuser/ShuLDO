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
    
    def scan_IinVinVout_CURR(self, regID1, regID2, file_name, max_Iin, inputPolarity, steps, stepSize):
        '''
        IV-scan in current supply mode.
        '''
        
        if 2*float(self.maximumInputCurrent) < float(max_Iin):
            print "ERROR: 2*maximumInputCurrent < max_Iin"
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
                        'Reg 1-'+regID1+' output voltage [V]', 'Reg 1-'+regID1+' output-reference ratio [1]', \
                        'Reg 2-'+regID2+' output voltage [V]', 'Reg 2-'+regID2+' output-reference ratio [1]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            inputCurr = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_current(inputPolarity*inputCurr, channel=1) #set Iin
                #
                input_current = inputCurr#misc.measure_current(1, 'Sourcemeter1')[0]    #measure Iin
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]          #measure Vin
                #
                load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]           #measure Iload_1
                load_current_2 = 0#misc.measure_current(1, 'Sourcemeter2')[0]           #measure Iload_2
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
                logging.info("Regulator 1-"+regID1+" output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 1-"+regID1+" output-reference voltage ratio is %r" % outputRefRatio1)
                logging.info("Regulator 2-"+regID2+" output voltage is %r V" % output_voltage_2)
                logging.info("Regulator 2-"+regID2+" output-reference voltage ratio is %r" % outputRefRatio2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, input_current_2, \
                                  output_voltage_1, outputRefRatio1, output_voltage_2, outputRefRatio2])
                f.writerow(misc.data[-1])
                #
                inputCurr += stepSize                                                                                   #Increase input current for next iteration
                if float(inputCurr) > float(max_Iin) or float(input_voltage) >= 1.85 or \
                   float(input_current_1) > float(self.maximumInputCurrent) or float(input_current_2) > float(self.maximumInputCurrent):  #Maximum values reached?
                    break
        
        logging.info('Measurement finished.')
        
        misc.reset(1, 'Sourcemeter1')
        misc.reset(2, 'Sourcemeter1')
        misc.reset(1, 'Sourcemeter2')
        misc.reset(1, 'Sourcemeter3')
        
        iv.livePlot(file_name)
    
    
    def scan_IinVinVout_VOLT(self, regID1, regID2, file_name, max_Vin, inputPolarity, steps, stepSize):
        '''
        IV-scan in voltage supply mode.
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
        dut['Sourcemeter1'].set_current_range(0.001, channel = 2)
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
                        'Reg 1-'+regID1+' output voltage [V]', 'Reg 1-'+regID1+' output-reference ratio [1]', \
                        'Reg 2-'+regID2+' output voltage [V]', 'Reg 2-'+regID2+' output-reference ratio [1]'])
            
            Rshunt = 0.01 #R02/03 on PCB
            
            inputVolt = 0
            #Measurement loop
            for x in range(0, int(steps)):
                dut['Sourcemeter1'].set_voltage(inputPolarity*inputVolt, channel=1) #set Vin
                #
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]          #measure Iin
                input_voltage = inputVolt#misc.measure_voltage(1, 'Sourcemeter1')[0]    #measure Vin
                #
                load_current_1 = 0#misc.measure_current(2, 'Sourcemeter1')[0]           #measure Iload_1
                load_current_2 = 0#misc.measure_current(1, 'Sourcemeter2')[0]           #measure Iload_2
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
                logging.info("Regulator 1-"+regID1+" output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 1-"+regID1+" output-reference voltage ratio is %r" % outputRefRatio1)
                logging.info("Regulator 2-"+regID2+" output voltage is %r V" % output_voltage_2)
                logging.info("Regulator 2-"+regID2+" output-reference voltage ratio is %r" % outputRefRatio2)
                #
                #Writing readout in output file
                misc.data.append([input_current, input_voltage, input_current_1, input_current_2, \
                                  output_voltage_1, outputRefRatio1, output_voltage_2, outputRefRatio2])
                f.writerow(misc.data[-1])
                #
                inputCurr += stepSize                                                                                   #Increase input current for next iteration
                if float(inputVolt) > float(max_Vin) or float(input_current) >= 2*float(self.maximumInputCurrent) or \
                   float(input_current_1) > 0.02 or float(input_current_2) > 0.02:                                      #Maximum values reached?
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
            elif "output voltage" in header[i] and "Reg 1" in header[i]:                    #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage 1 in column %r" % i)
            elif "output voltage" in header[i] and "Reg 2" in header[i]:                    #Beware: lower case "o" in output voltage!
                Vout2 = i
                logging.info("Output voltage 2 in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        V_out1 = [None]*len(csvfilearray)
        V_out2 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                V_out1[i] = csvfilearray[i][Vout1]
                V_out2[i] = csvfilearray[i][Vout2]
            except AttributeError:
                pass
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(I_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            plt.plot(I_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'First Reg. Output Voltage')
            plt.plot(I_in, V_out2, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Second Reg. Output Voltage')
            plt.axis([0,2*self.maximumInputCurrent,0,2.0])
            plt.xlabel('Input Current / A')
            plt.ylabel('Voltage / V')
        elif "VOLT" in file_name:
            #plt.plot(V_in, I_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Current')
            plt.plot(V_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'First Reg. Output Voltage')
            plt.plot(V_in, V_out2, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Second Reg. Output Voltage')
            plt.axis([0,1.9,0,2.0])
            plt.xlabel('Input Voltage / V')
            plt.ylabel('Voltage / V')
        
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
    print 'Sourcemeter 3: '+dut['Sourcemeter3'].get_name()
    
    raw_input("Proceed?")
    
    iv = IV()
#    iv.maximumInputCurrent = 1.0    #1A chip
    iv.maximumInputCurrent = 2.0    #2A chip
    
    regId1 = '1'
    regId2 = '1'
    
    
#    fileName = "output/IV_CURR/IV_CURR_Vref1_600mV_Vref2_500mV_REG1-"+regId1+"_REG2-"+regId2+".csv"
    fileName = "output/IV_CURR/IV_CURR_Vref1_600mV_Vref2_500mV_Voff1_1000mV_Voff2_1000mV.csv"
    
    #scan_IinVinVout_CURR(  regID1, regID2, file_name, max_Iin, inputPolarity, steps, stepSize)
    iv.scan_IinVinVout_CURR(regId1, regId2, fileName,  3.0,     1,             60,    0.05)
    
#    fileName = "output/IV_VOLT_Iload_0mA_Vref_600mV_REG"+chipId+"-"+regId+".csv"
    
    #scan_IinVinVout_VOLT(  regID1, regID2, file_name, max_Vin, inputPolarity, steps, stepSize)
#    iv.scan_IinVinVout_VOLT(regId1, regId2, fileName,  1.8,     1,             72,    0.025)
