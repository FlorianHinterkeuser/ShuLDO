'''
Created on 05.10.2016

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path

from scan_misc import Misc
from basil.dut import Dut


class LoadReg(object):
    

    '''
    Class to perform a standard IV scan of the FE65 ShuLDO. For the standalone scan (current supply mode), one regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
    in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
    voltage drop due to R02 can be calculated using the input current and Ohm's law.
    The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21). 
    '''

    
    
    def scan_loadreg_CURR(self, file_name, max_Iload, polarity, steps , stepsize, Iin, *device):
        '''
        IV-scan in current supply mode. One regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
        in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
        voltage drop due to R02 can be calculated using the input current and Ohm's law.
        The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21).
        For a parallel scan, a second regulator is set to current supply mode. The maximum allowed input current has to be adjusted accordingly (x2).
        '''
        time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        misc.reset(*device)                                          #resetting the Sourcemeters
        
        misc.set_source_mode('CURR', 2, 1.5, 1.5, *device)          #set current source mode for every sourcemeter

        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            #file_name = file_name.split('_')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
            
        pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Iload, poll=10, term_width=80).start()               #fancy progress bar
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Regulator 1 load current [A]', 'Regulator 2 output voltage[V]'])                      #What is written in the output file
            #f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Regulator 1 load current [A]')                      #What is written in the output file
            if Iin <= 1.05 and Iin >= 0:
                dut['Sourcemeter1'].set_current(Iin)
                logging.info('Input current set to %f A' % (Iin))
            else:
                dut['Sourcemeter1'].set_current(0.5)
                logging.info('Desired input current too high, set to 0.5 A')
            #input_current = misc.measure_current('Sourcemeter1')                                                                                                #Check input current
            dut['Sourcemeter1'].four_wire_on()
            dut['Sourcemeter2'].four_wire_on()
            dut['Sourcemeter3'].four_wire_on()
            iload = 0
            for x in range(0, int(steps)):                                                                                                                      #loop over steps                                                                
                dut['Sourcemeter2'].set_current(polarity*iload)                                                                                                  #Set input current
                time.sleep(0.01)
                input_current = misc.measure_current('Sourcemeter1')[0]                                                                                          #Value of interest is in the [0] position of the readout list
                time.sleep(0.01)
                input_voltage = misc.measure_voltage('Sourcemeter1')[0]
                output_voltage_1 = misc.measure_voltage('Sourcemeter2')[0]
                time.sleep(0.01)
                load_current = misc.measure_current('Sourcemeter2')[0]
                output_voltage_2 = misc.measure_voltage('Sourcemeter3')[0]
                output_current_2 = misc.measure_current('Sourcemeter3')[0]
                logging.info("Input current is %f A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %f V" % input_voltage)
                logging.info("Regulator 1 output voltage is %f V" % output_voltage_1)
                logging.info("Regulator 1 load current is %f A" % load_current)
                logging.info("Regulator 2 output voltage is %f V" % output_voltage_2)
                logging.info("Regulator 2 load current is %f A" % output_current_2)
                misc.data.append([input_voltage, input_current, output_voltage_1, load_current, output_voltage_2])                                                          #Writing readout in output file
                f.writerow(misc.data[-1])
                pbar.update(iload)
                iload += stepsize                                                                                                                               #Increase input current for next iteration
                if iload >= max_Iload or input_voltage >= 1.99:                                                                                                #Maximum values reached?
                    break             
    
            
            
            pbar.finish()
            logging.info('Measurement finished, plotting ...')
            misc.reset(*device)
        
        
    def scan_loadreg_VOLT(self, file_name, max_Iload, polarity, steps , stepsize, Vin, *device):
        '''
        IV-scan in voltage supply mode. All regulators are used in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current.
        The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
        voltage drop due to R02 can be calculated using the input current and Ohm's law.
        The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21).
        For a parallel scan, [to be continued].
        '''
        #time.sleep(misc.minimum_delay)
        logging.info("Starting ...")
        
        misc.reset(*device)                                          #resetting the Sourcemeters
        dut['Sourcemeter1'].four_wire_on()
        dut['Sourcemeter2'].four_wire_on()
        
        misc.set_source_mode('VOLT', 0.5, 0.5, 0.5, 'Sourcemeter1')          #set current source mode for every sourcemeter
        misc.set_source_mode('CURR', 1.5, 1.5, 1.5, 'Sourcemeter2')
        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            #file_name = file_name.split('_')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
            
        pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Iload, poll=10, term_width=80).start()               #fancy progress bar
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Regulator 1 load current [V]'])                      #What is written in the output file
            input = 0
            if Vin < 2 and Vin >= 0:
                dut['Sourcemeter1'].set_voltage(Vin)
            else:
                raise RuntimeError('Input voltage too high!')
            for x in range(0, int(steps)):                                                                                                                      #loop over steps                                                                                                                                                                #Set input voltage
                dut['Sourcemeter2'].set_current(polarity*input)
                time.sleep(0.01)
                input_current = misc.measure_current('Sourcemeter1')[0]                                                                                          #Value of interest is in the [0] position of the readout list
                time.sleep(0.01)
                input_voltage = misc.measure_voltage('Sourcemeter1')[0]
                output_voltage_1 = misc.measure_voltage('Sourcemeter2')[0]
                time.sleep(0.01)
                load_current = misc.measure_current('Sourcemeter2')[0]
                #output_voltage_2 = misc.measure_voltage('Sourcemeter3')[0]
                logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %r V" % input_voltage)
                logging.info("Regulator 1 load current is %f A" % load_current)
                logging.info("Regulator 1 output voltage is %r V" % output_voltage_1)
                #logging.info("Regulator 2 output voltage is %r V" % output_voltage_2)
                misc.data.append([input_voltage, input_current, output_voltage_1, load_current])                                                          #Writing readout in output file
                f.writerow(misc.data[-1])
                pbar.update(input)
                input += stepsize                                                                                                                               #Increase input current for next iteration
                if input >= max_Iload or float(input_voltage) >= 2 or float(output_voltage_1) >= 1.4:                                                                                                #Maximum values reached?
                    break             
    
            
            
            pbar.finish()
            logging.info('Measurement finished, plotting ...')
            misc.reset(*device)
        
        
        
        
        
        

if __name__ == '__main__':
    
    dut = Dut('devices.yaml')
    dut.init()
    misc = Misc(dut=dut)                                                                                                                                        #Calling scan_misc with dut = Dut('devices.yaml')
    
    print dut['Sourcemeter1'].get_name()                                                                                                                        #Get meter ID to check communication
    print dut['Sourcemeter2'].get_name()
    #print dut['Sourcemeter3'].get_name()
    #print dut['Sourcemeter3'].get_name()
    
    

    
    iv = LoadReg()
    #iv.scan_IinVinVout_CURR('test', 0.005, 1, 10 , 0.0005, 'Sourcemeter1', 'Sourcemeter2')                                                                   #Conduct IV scan
    #iv.scan_IinVinVout_VOLT('test', 0.5, 1, 10 , 0.05, 'Sourcemeter1', 'Sourcemeter2') 
    iv.scan_loadreg_CURR('CMode_500_600_mV_LoadReg.csv', 0.5, -1, 5000 , 0.001, 1, 'Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3')    
    #iv.scan_loadreg_VOLT('VMode_600_mV_LoadReg.csv', 0.49, -1, 5000 , 0.001, 1.5, 'Sourcemeter1', 'Sourcemeter2')
    