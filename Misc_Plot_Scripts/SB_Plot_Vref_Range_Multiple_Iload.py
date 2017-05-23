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

class IV(object):
    
    '''
    Class to perform a standard IV scan of the FE65 ShuLDO.
    '''
    
    def livePlot(self):
        fileNames = ["Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_0mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_100mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_200mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_300mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_400mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_VOLT/Vref_Range_VOLT_Vin_1900mV_load_500mA.csv"]
        
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
                elif "output voltage" in header[i] and "1" in header[i]:                    #Beware: lower case "o" in output voltage!
                    Vout1 = i
                    logging.info("Output voltage 1 in column %r" % i)
            
            
            V_ref1 = [None]*len(csvfilearray)
            V_out1 = [None]*len(csvfilearray)
            Ratio_1 = [None]*len(csvfilearray)
            
            for i in range(0, len(csvfilearray)):
                try:
                    V_ref1[i] = csvfilearray[i][Vref1]
                    V_out1[i] = csvfilearray[i][Vout1]
                    Ratio_1[i] = float(V_out1[i])/float(V_ref1[i])
                except AttributeError:
                    pass
            
            IloadStr = file_name.split("_load_")[1].split(".csv")[0]
            
            if "CURR" in file_name or "VOLT" in file_name:
                plt.plot(V_ref1, V_out1, ".-", markersize=3, linewidth=0.5, label="Output Voltage (Iload="+IloadStr+")")
                ##plt.plot(V_ref1, Ratio_1, ".-", markersize=3, linewidth=0.5, label="Output-Reference-Ratio (Iload="+IloadStr+")")
            else:
                print "Data not found"
        
        plt.axis([0.45,0.625,0.9,1.3])
        ##plt.axis([0.45,0.625,1.95,2.05])
        ##plt.axis([0.45,0.625,1.9,2.05])
        plt.legend()
        plt.savefig(fileNames[0].split("_load_")[0]+".pdf")
        ##plt.savefig(fileNames[0].split("_load_")[0]+"_ratio.pdf")


if __name__ == '__main__':
    
    iv = IV()

    iv.livePlot()
