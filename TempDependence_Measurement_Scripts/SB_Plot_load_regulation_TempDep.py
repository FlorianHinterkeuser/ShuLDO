'''
Created on 26.09.2016

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import os.path
import numpy as np

from scan_misc import Misc
from basil.dut import Dut

class IV(object):
    
    '''
    Class to draw load regulation curves for multiple ambient temperatures in one diagram
    '''
        
    def livePlot(self, Iin, Vref, Voffs):
        fileNames = ["output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-30C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-26C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-22C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-18C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-14C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-10C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-6C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_-2C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_2C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_6C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_10C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_14C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_18C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_22C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_26C.csv", \
                     "output/Load_Regulation_CURR/Loadreg_CURR_Iin_"+Iin+"mA_Vref_"+Vref+"mV_Voffs_"+Voffs+"mV_Temp_30C.csv"]
        
        
        NUM_COLORS = 16
        
        cm = plt.get_cmap('rainbow')
        cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
        scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(NUM_COLORS)])
        
        
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
                elif "load current" in header[i]:
                    Iload1 = i
                    logging.info("load current in column %r" % i)
                elif "output voltage" in header[i]:                         #Beware: lower case "o" in output voltage!
                    Vout1 = i
                    logging.info("Output voltage in column %r" % i)
                elif "Temp-Sensor 1" in header[i]:
                    T1 = i
                    logging.info("Temperature 1 in column %r" % i)
                elif "Temp-Sensor 2" in header[i]:
                    T2 = i
                    logging.info("Temperature 2 in column %r" % i)
            
            
            V_in = [None]*len(csvfilearray)
            I_load1 = [None]*len(csvfilearray)
            V_out1 = [None]*len(csvfilearray)
            V_drop1 = [None]*len(csvfilearray)
            T_1 = [None]*len(csvfilearray)
            T_2 = [None]*len(csvfilearray)
            
            
            for i in range(0, len(csvfilearray)):
                try:
                    V_in[i] = csvfilearray[i][Vin]
                    I_load1[i] = csvfilearray[i][Iload1]
                    V_out1[i] = csvfilearray[i][Vout1]
                    T_1[i] = csvfilearray[i][T1]
                    T_2[i] = csvfilearray[i][T2]
                except AttributeError:
                    pass
                V_drop1[i] = float(V_in[i]) - float(V_out1[i])
            
            
            temperature = file_name.split("_Temp_")[1].split(".csv")[0]
            
            ax.plot(I_load1, V_out1, ".-", markersize=0, linewidth=0.5, label= 'Output Voltage (T='+temperature+')')
            #ax.plot(I_load1, V_in, ".-", markersize=0, linewidth=0.5, label = 'Input Voltage (T='+temperature+')')
        
        vout_th = 2*float(fileNames[0].split("_Vref_")[1].split("mV_Voffs_")[0])/1000
        
        plt.xlabel('Load Current / A')
        plt.ylabel('Output Voltage / V')
        ax.axis([0,1.0,vout_th-0.05,vout_th+0.05])
        #ax.legend()
        ax.grid(True)
        fig.savefig(fileNames[0].split("_Temp_")[0]+".pdf")



if __name__ == '__main__':
    
    iv = IV()
    #  livePlot(Iin,    Vref,  Voffs)
    iv.livePlot("860",  "500", "800")
    
    iv = IV()
    #  livePlot(Iin,    Vref,  Voffs)
    iv.livePlot("1130", "600", "600")
    
    iv = IV()
    #  livePlot(Iin,    Vref,  Voffs)
    iv.livePlot("860",  "600", "800")
    
    iv = IV()
    #  livePlot(Iin,    Vref,  Voffs)
    iv.livePlot("1000", "600", "1000")
    
    iv = IV()
    #  livePlot(Iin,    Vref,  Voffs)
    iv.livePlot("1000", "600", "1200")
