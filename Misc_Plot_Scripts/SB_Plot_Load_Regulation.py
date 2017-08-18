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
        fileNames = ["output/Load_Regulation_CURR/Loadreg_CURR_Iin_500mA_Vref_600mV.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_550mA_Vref_600mV.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_600mA_Vref_600mV.csv", \
                     #"output/Load_Regulation_CURR/Loadreg_CURR_Iin_625mA_Vref_600mV.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_650mA_Vref_600mV.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_700mA_Vref_600mV.csv"]

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
                if "Input voltage" in header[i]:
                    Vin = i
                    logging.info("Input voltage in column %r" % i)
                elif "Input current" in header[i]:
                    Iin = i
                    logging.info("Input current in column %r" % i)
                elif "output voltage" in header[i] and "1" in header[i]:                    #Beware: lower case "o" in output voltage!
                    Vout1 = i
                    logging.info("Output voltage 1 in column %r" % i)
                elif "load current" in header[i]:
                    Iload1 = i
                    logging.info("Load current 1 in column %r" % i)
            
            V_in = [None]*len(csvfilearray)
            I_in = [None]*len(csvfilearray)
            V_out1 = [None]*len(csvfilearray)
            I_load1 = [None]*len(csvfilearray)
            
            
            for i in range(0, len(csvfilearray)):
                try:
                    V_in[i] = csvfilearray[i][Vin]
                    I_in[i] = csvfilearray[i][Iin]
                    V_out1[i] = csvfilearray[i][Vout1]
                    I_load1[i] = csvfilearray[i][Iload1]
                except AttributeError:
                    pass
            
            saveFileName = ""
            
            if "CURR" in file_name:
                IinStr = file_name.split("_Iin_")[1].split("_Vref_")[0]
                saveFileName = fileNames[0].split("_Iin_")[0]+"_Vref_"+fileNames[0].split("_Vref_")[1]+".pdf"
                #plt.plot(I_load1, V_in, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'Input Voltage')
                plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, label = 'Output Voltage (Iin='+IinStr+')')
                plt.axis([0,0.5,1.18,1.22])
            elif "VOLT" in file_name:
                VinStr = file_name.split("_Vin_")[1].split("_Vref_")[0]
                saveFileName = fileNames[0].split("_Vin_")[0]+"_Vref_"+fileNames[0].split("_Vref_")[1]+".pdf"
                plt.plot(I_load1, V_out1, ".-", markersize=3, linewidth=0.5, label= 'Output Voltage (Vin='+VinStr+')')
                plt.axis([0,0.5,1,1.25])
            else:
                print "Data not found"
        
        plt.legend()
        plt.savefig(saveFileName)


if __name__ == '__main__':
    
    iv = IV()

    iv.livePlot()
