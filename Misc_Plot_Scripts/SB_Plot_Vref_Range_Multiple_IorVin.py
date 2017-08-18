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
        fileNames = [#"Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_500mA_load_500mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_600mA_load_500mA.csv", \
                     "Outputs/Single_Chip_Board/Vref_Range_CURR/Vref_Range_CURR_Iin_700mA_load_500mA.csv"]
        
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
            
            saveFileName = ""
            
            #plot Vout
            if "CURR" in file_name:
                IinStr = file_name.split("_Iin_")[1].split("_load_")[0]
                saveFileName = fileNames[0].split("_Iin_")[0]+"_load_"+fileNames[0].split("_load_")[1]+".pdf"
                plt.plot(V_ref1, V_out1, ".-", markersize=3, linewidth=0.5, label="Iin="+IinStr)
                plt.ylabel("Output Voltage / V")
                plt.axis([0.46,0.62,0.9,1.3])
            elif "VOLT" in file_name:
                VinStr = file_name.split("_Vin_")[1].split("_load_")[0]
                saveFileName = fileNames[0].split("_Vin_")[0]+"_load_"+fileNames[0].split("_load_")[1]+".pdf"
                plt.plot(V_ref1, V_out1, ".-", markersize=3, linewidth=0.5, label="Vin="+VinStr)
                plt.ylabel("Output Voltage / V")
                plt.axis([0.46,0.62,0.9,1.3])
            else:
                print "Data not found"

#            #plot Ratio
#            if "CURR" in file_name:
#                IinStr = file_name.split("_Iin_")[1].split("_load_")[0]
#                saveFileName = fileNames[0].split("_Iin_")[0]+"_load_"+fileNames[0].split("_load_")[1]+"_ratio.pdf"
#                plt.plot(V_ref1, Ratio_1, ".-", markersize=3, linewidth=0.5, label="Iin="+IinStr)
#                plt.ylabel("Output-Reference-Ratio")
#                plt.axis([0.46,0.62,1.95,2.00])
#            elif "VOLT" in file_name:
#                VinStr = file_name.split("_Vin_")[1].split("_load_")[0]
#                saveFileName = fileNames[0].split("_Vin_")[0]+"_load_"+fileNames[0].split("_load_")[1]+"_ratio.pdf"
#                plt.plot(V_ref1, Ratio_1, ".-", markersize=3, linewidth=0.5, label="Vin="+VinStr)
#                plt.ylabel("Output-Reference-Ratio")
#                plt.axis([0.46,0.62,1.95,2.00])
#            else:
#                print "Data not found"
        
        plt.xlabel("Reference Voltage / V")
        plt.legend()
        plt.savefig(saveFileName)


if __name__ == '__main__':
    
    iv = IV()

    iv.livePlot()
