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

class IV(object):
    
    '''
    Class to perform a standard IV scan of the FE65 ShuLDO.
    '''
    
    def livePlot(self):
        fileNames = ["Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_0mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_100mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_200mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_300mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_400mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_480mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_490mA.csv"]
        
        plt.grid(True)
        
        for file_name in fileNames:
            csvfilearray = []
            header = []
            file = []
            with open(file_name, 'rb') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                header = next(plots)
                for row in plots:
                    csvfilearray.append(row)
            for i in range(0, len(header)):
                if "reference voltage" in header[i]:
                    Vref1 = i
                    logging.info("Reference voltage 1 in column %r" % i)
                elif "Input current" in header[i]:                          #Beware: lower case "o" in output voltage!
                    Iin = i
                    logging.info("Input current in column %r" % i)
                elif "Input voltage" in header[i]:
                    Vin = i
                    logging.info("Reference voltage 1 in column %r" % i)
            
            
            V_ref1 = [None]*len(csvfilearray)
            R_in = [None]*len(csvfilearray)
            
            for i in range(0, len(csvfilearray)):
                try:
                    V_ref1[i] = csvfilearray[i][Vref1]
                    R_in[i] = float(csvfilearray[i][Vin])/float(csvfilearray[i][Iin])
                except AttributeError:
                    pass
            
            IloadStr = file_name.split("_load_")[1].split(".csv")[0]
            
            if "CURR" in file_name or "VOLT" in file_name:
                plt.plot(V_ref1, R_in, ".-", markersize=3, linewidth=0.5, label="Iload="+IloadStr)
                ##plt.plot(V_ref1, Ratio_1, ".-", markersize=3, linewidth=0.5, label="Output-Reference-Ratio (Iload="+IloadStr+")")
            else:
                print "Data not found"
        
        plt.axis([0.46,0.625,2.8,3.05])
        plt.xlabel("Reference Voltage / V")
        plt.ylabel("Input Impedance / Ohm")
        plt.legend()
        plt.savefig(fileNames[0].split("_load_")[0]+"_InputImpedance.pdf")


if __name__ == '__main__':
    
    iv = IV()

    iv.livePlot()
