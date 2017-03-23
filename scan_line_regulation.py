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
from Plot import Plot

from scan_misc import Misc
from basil.dut import Dut

class IV(object):    

    '''
    Class to perform a standard IV scan of the FE65 ShuLDO. For the standalone scan (current supply mode), one regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
    in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between  PCB GND and P03 (HI).
    The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21). 
    '''
    
    
    def scan_IinVinVout_CURR(self, file_name, max_Iin, polarity, steps , stepsize, load, vref, vofs, *device):
        '''
        IV-scan in current supply mode. One regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
        in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
        voltage drop due to R02 can be calculated using the input current and Ohm's law.
        The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21).
        For a parallel scan, a second regulator is set to current supply mode. The maximum allowed input current has to be adjusted accordingly (x2).
        '''
        
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        misc.reset(1, *device)                               #Sourcemeter Reset: reset(channel, *device). If two-channel meters are used, call reset() again for each additional channel.
        misc.reset(2, *device)
        
        misc.set_source_mode('CURR', 1, *device)          #set current source mode for every sourcemeter. If two-channel meters are used, call again for additional channels.
        misc.set_source_mode('VOLT', 2, 'Sourcemeter1')
        dut['Sourcemeter1'].four_wire_on(channel=1)
        dut['Sourcemeter2'].four_wire_on()                  #4-wire sensing.
        
        dut['Sourcemeter1'].set_voltage_limit(2, channel = 1)       #Set compliance limits
        dut['Sourcemeter1'].set_current_limit(0.1, channel = 2)        
        dut['Sourcemeter2'].set_voltage_limit(2)
        
        dut['Sourcemeter1'].set_current_range(3, channel = 1)       #Set source range
        dut['Sourcemeter1'].set_voltage_range(2, channel = 2)
        dut['Sourcemeter2'].set_autorange()

        dut['Sourcemeter1'].on(channel=1)
        dut['Sourcemeter1'].on(channel=2)
        dut['Sourcemeter2'].on()

        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
        input = 0
        #dut['Sourcemeter1'].set_voltage(vref, channel = 2)                #Use this to set a reference voltage rather than measuring it. Or, use a multimeter to measure it.
        dut['Sourcemeter1'].set_voltage(vofs, channel = 2)                #Use this to set an offset voltage rather than measuring it. Or, use a multimeter to measure it.
        
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Load current [A]'])                      #What is written in the output file
            
            for x in range(0, int(steps)):                                                                                                                 #Measurement loop                                                                
                dut['Sourcemeter1'].set_current(polarity*input, channel=1)       
                input_current = misc.measure_current(1, 'Sourcemeter1')[0]
                input_voltage = misc.measure_voltage(1, 'Sourcemeter1')[0]
                output_voltage_1 = misc.measure_voltage(1, 'Sourcemeter2')[0]
                #load_current = misc.measure_current(1, 'Sourcemeter2')[0]
                load_current = 0                                                        #Speedup
                logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1 output voltage is %r V" % output_voltage_1)
                logging.info("Regulator 1 load current is %r A" % load_current)
                #print "Reference voltage is %f V" % reference_voltage
                misc.data.append([input_voltage, input_current, output_voltage_1, load_current])                                                          #Writing readout in output file
                f.writerow(misc.data[-1])
                input += stepsize                                                                                                                               #Increase input current for next iteration
                if input > max_Iin or float(input_voltage) >= 1.99:                                                                                                #Maximum values reached?
                    break             
     
        logging.info('Measurement finished')
       
        misc.reset(1, *device)
        misc.reset(2, *device)
                    
        
    def LivePlot(self, file_name):
        csvfilearray = []
        header = []
        file = []
        
        Iload1 = 0
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
            elif "output voltage" in header[i] and "1" in header[i]:                    #Beware: lower case "o" in output voltage!
                Vout1 = i
                logging.info("Output voltage 1 in column %r" % i)
            try:
                if "load current" in header[i]:
                    Iload1 = i
                    logging.info("Load current in column %r" % i)
            except:
                if "load current" not in header[i]:
                    Iload1 = 0
                    logging.info("No load current applied")

                
        V_in = [None]*len(csvfilearray) 
        I_in = [None]*len(csvfilearray) 
        V_out1 = [None]*len(csvfilearray)
        I_load1 = [None]*len(csvfilearray) 
        load = [None] * len(csvfilearray)
        V_drop = [None] * len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                V_out1[i] = csvfilearray[i][Vout1]
                I_load1[i] = csvfilearray[i][Iload1]
            except AttributeError:
                pass
            V_drop[i] = float(V_in[i]) - float(V_out1[i])
        
        if "IV" in file_name:
            plt.grid(True)
            plt.plot(I_in, V_out1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Output Voltage')
            
            plt.plot(I_in, V_in, ".-", markersize=3, linewidth=0.5, color = 'b', label = 'Input Voltage')
            plt.plot(I_in, V_drop, ".-", markersize=3, linewidth=0.5, color = 'g', label = 'Dropout Voltage')
            plt.axis([0,1.5,0,1.75])
            plt.legend()
            plt.savefig(file_name + '.pdf')
        else:
            print "Data not found"
          
    def testfunction(self, *device):                #Devicetest: identifier
        print dut['Sourcemeter1'].get_name()    
        
        

if __name__ == '__main__':
    
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)                                                                                                                                      #Calling scan_misc with dut = Dut('devices.yaml')
    
    #print dut['Sourcemeter1'].get_name()                                                                                                                        #Get meter ID to check communication
    #print dut['Sourcemeter2'].get_name()
    #print dut['Sourcemeter3'].get_name()
    
    

    
    iv = IV()
    #iv.LivePlot('CMode_600_500_mV_LoadReg.csv')
    
    iv.scan_IinVinVout_CURR("IV_CURR_load_0mA_vref_600_vofs_600.csv", 1.01, 1, 20 , 0.05, 0, 0.6, 0.6, 'Sourcemeter1', 'Sourcemeter2')    #scan_IinVinVout_CURR(file_name, max_Iin, polarity, steps, stepsize, load, vref, vofs, *device)
    iv.LivePlot("IV_CURR_load_0mA_vref_600_vofs_600.csv")
    iv.scan_IinVinVout_CURR("IV_CURR_load_0mA_vref_600_vofs_800.csv", 1.01, 1, 20 , 0.05, 0, 0.6, 0.8, 'Sourcemeter1', 'Sourcemeter2')    #scan_IinVinVout_CURR(file_name, max_Iin, polarity, steps, stepsize, load, vref, vofs, *device)
    iv.LivePlot("IV_CURR_load_0mA_vref_600_vofs_800.csv")
                                                                      
