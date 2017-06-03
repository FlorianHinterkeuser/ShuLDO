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
    
    def livePlot(self, file_name, dynLoadChipID):
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
            elif "input current" in header[i] and "Reg 1" in header[i]:
                Iin1 = i
                logging.info("Input current 1 in column %r" % i)
            elif "input current" in header[i] and "Reg 2" in header[i]:
                Iin2 = i
                logging.info("Input current 2 in column %r" % i)
            elif "load current" in header[i] and "Reg 1" in header[i]:
                Iload1 = i
                logging.info("Load current 1 in column %r" % i)
            elif "load current" in header[i] and "Reg 2" in header[i]:
                Iload2 = i
                logging.info("Load current 2 in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        I_in1 = [None]*len(csvfilearray)
        I_in2 = [None]*len(csvfilearray)
        I_load1 = [None]*len(csvfilearray)
        I_load2 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                I_in1[i] = csvfilearray[i][Iin1]
                I_in2[i] = csvfilearray[i][Iin2]
                I_load1[i] = csvfilearray[i][Iload1]
                I_load2[i] = csvfilearray[i][Iload2]
            except AttributeError:
                pass
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            if dynLoadChipID == '1':
                plt.plot(I_load1, I_in1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'First Reg. Input Current')
                plt.plot(I_load1, I_in2, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Second Reg. Input Current')
                plt.xlabel('First Reg. Load Current / A')
            elif dynLoadChipID == '2':
                plt.plot(I_load2, I_in1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'First Reg. Input Current')
                plt.plot(I_load2, I_in2, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Second Reg. Input Current')
                plt.xlabel('Second Reg. Load Current / A')

        #plt.axis([0,1.5,0,2.0])
        plt.ylabel('Regulator Input Current / A')
        plt.legend()
        plt.savefig('output/Load_Regulation_Current_Distribution/Loadreg_CurrentDist_CURR'+file_name.split("output/Load_Regulation_CURR/Loadreg_CURR")[1] + '.pdf')


if __name__ == '__main__':
    
    iv = IV()
    
    regId1 = '2'
    regId2 = '1'
    #
    dynLoad_ChipId = '1'
    
#    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_1000mA_Vref1_600mV_Vref2_500mV_REG1-"+regId1+"_REG2-"+regId2+".csv"
    fileName = "output/Load_Regulation_CURR/Loadreg_CURR_Iin_2200mA_Vref1_600mV_Vref2_600mV_Voff1_600mV_Voff2_800mV.csv"
    if dynLoad_ChipId == '2':
        fileName = fileName.split(".csv")[0] + "_1.csv"
    
    iv.livePlot(fileName, dynLoad_ChipId)
