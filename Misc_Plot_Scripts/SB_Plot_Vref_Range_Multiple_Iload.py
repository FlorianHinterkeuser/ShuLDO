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
        fileNames = ["Vref_Range_CURR_Iin_1130mA_Iload_0mA_Voff_600mV.csv", \
                     #"Vref_Range_CURR_Iin_1000mA_Iload_450mA_Voff_1000mV.csv", \
                     "Vref_Range_CURR_Iin_1130mA_Iload_1000mA_Voff_600mV.csv"]
        
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
                if "Reference voltage" in header[i]:
                    Vref1 = i
                    logging.info("Reference voltage 1 in column %r" % i)
                elif "output voltage" in header[i]:                    #Beware: lower case "o" in output voltage!
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
            
            IloadStr = file_name.split("_Iload_")[1].split("_Voff")[0]
            
#            #plot Vout
#            if "CURR" in file_name or "VOLT" in file_name:
#                plt.plot(V_ref1, V_out1, ".-", markersize=3, linewidth=0.5, label="Iload="+IloadStr)
#            else:
#                print "Data not found"
#        
#        plt.axis([0.46,0.62,0.9,1.25])
#        plt.xlabel("Reference Voltage / V")
#        plt.ylabel("Output Voltage / V")
#        plt.legend()
#        plt.savefig(fileNames[0].split("_load_")[0]+".pdf")

            #plot Ratio
            if "CURR" in file_name or "VOLT" in file_name:
                plt.plot(V_ref1, Ratio_1, ".-", markersize=3, linewidth=0.5, label="Iload="+IloadStr)
            else:
                print "Data not found"
        
        plt.axis([0.5,0.6,1.5,2.00])
        plt.xlabel("Reference Voltage / V")
        plt.ylabel("Vout / Vref")
        plt.legend()
        plt.savefig(fileNames[0].split("_Iload_")[0]+"_Voff_"+fileNames[0].split("_Voff_")[1]+"_ratio.pdf")


if __name__ == '__main__':
    
    iv = IV()

    iv.livePlot()
