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
            elif "input current" in header[i] and "Reg 1" in header[i]:
                Iin1 = i
                logging.info("Input current 1 in column %r" % i)
            elif "input current" in header[i] and "Reg 2" in header[i]:
                Iin2 = i
                logging.info("Input current 2 in column %r" % i)
        
        
        V_in = [None]*len(csvfilearray)
        I_in = [None]*len(csvfilearray)
        I_in1 = [None]*len(csvfilearray)
        I_in2 = [None]*len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                V_in[i] = csvfilearray[i][Vin]
                I_in[i] = csvfilearray[i][Iin]
                I_in1[i] = csvfilearray[i][Iin1]
                I_in2[i] = csvfilearray[i][Iin2]
            except AttributeError:
                pass
        
        
        plt.grid(True)
        
        if "CURR" in file_name:
            plt.plot(I_in, I_in1, ".-", markersize=3, linewidth=0.5, color = 'r', label= 'First Reg. Input Current')
            plt.plot(I_in, I_in2, ".-", markersize=3, linewidth=0.5, color = 'g', label= 'Second Reg. Input Current')
            #plt.axis([0,1.5,0,2.0])
            plt.xlabel('Total Input Current / A')
            plt.ylabel('Regulator Input Current / A')
        
        plt.legend()
        plt.savefig('output/Powerup_Current_Distribution/Powerup_CurrentDist_CURR'+file_name.split("output/IV_CURR/IV_CURR")[1] + '.pdf')


if __name__ == '__main__':
    
    iv = IV()
    
    regId1 = '2'
    regId2 = '1'
    
#    fileName = "output/IV_CURR/IV_CURR_Vref1_600mV_Vref2_600mV_REG1-"+regId1+"_REG2-"+regId2+".csv"
    fileName = "output/IV_CURR/IV_CURR_Vref1_600mV_Vref2_600mV_Voff1_800mV_Voff2_800mV.csv"
    
    iv.livePlot(fileName)
