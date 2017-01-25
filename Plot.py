'''

@author: Wilhelm Linac
'''

import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path
import numpy as np

from basil.dut import Dut


class Plot(object):
    
    dir = os.getcwd()
    
    def __init__(self, nf):
        self.x = [[]]
        self.y = [[]]
        self.z = [[]]
        self.v = [[]]
        self.w = [[]]
        self.V_in = []
        self.V_out1 = []
        self.V_out2 = []
        self.I_in = []
        self.I_load1 = []
        self.result = []
        self.nf = nf
    
    def Readout(self, Vin, Iin, Vout1, file):
        nf = len(file)
        self.x = [[] for x in range(0, nf)]
        self.y = [[] for y in range(0, nf)]
        self.z = [[] for z in range(0, nf)]
        self.v = [[] for v in range(0, nf)]
        self.w = [[] for w in range(0, nf)]
        csvfilearray = [[] for csvfilearray in range(0, nf)]
        csvfile = [None] * nf
        plots = [None] * nf
        label = []
        color = []
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
            
        for i in range(0,nf):
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    csvfilearray[i].append(row)
                    if 'Regulator 2 output voltage[V]' in csvfilearray[0] and 'Regulator 1 load current [A]' in csvfilearray[0]:
                        Iload1 = 3
                        Vout2 = 4
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.v[i].append(row[Iload1])
                        self.w[i].append(row[Vout2])
                    elif 'Regulator 1 load current [A]' in csvfilearray[0] and 'Regulator 2 output voltage[V]' not in csvfilearray[0]:
                        Iload1 = 3
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.v[i].append(row[Iload1])
                    elif 'Regulator 1 load current [A]' not in csvfilearray[0] and 'Regulator 2 output voltage[V]' in csvfilearray[0]:
                        Vout2 = 2
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.w[i].append(row[Vout2])                    
                    elif 'Regulator 1 load current [A]' not in csvfilearray[0] and 'Regulator 2 output voltage[V]' not in csvfilearray[0]:
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                    else:
                        raise RuntimeError('Error occured')
        for i in range(0, nf):
            pass
        self.result = [self.x, self.y, self.z, self.v, self.w]
        #print self.result
        
        return self.result
        
    def Create_Axes(self, Vin, Iin, Vout1, Vout2, file, label):
        
        
        self.Readout(Vin, Iin, Vout1, file)                                     #L2C Issue 
        print self.result[0]
        print self.result[4]
        self.V_in = self.result[0]
        self.I_in = self.result[1]
        self.V_out1 = self.result[2]
        self.I_load1 = self.result[3]
        self.V_out2 = self.result[4]
        
        Output1 = self.V_out1
        for i in range(0, len(file)):
            for j in range(0, len(self.V_out1[i])):
                if float(self.V_out1[i][j]) > 1000:
                    self.V_out1[i][j] = float(self.V_out1[i][j])/1000
                    if float(self.V_out1[i][j]) < 1:
                        raise RuntimeError
                        
        #=======================================================================
        # for i in range(0, len(file)):
        #     plt.figure(1)
        #     plt.plot(I_in[i], V_out1[i], label = label[i])
        #     plt.grid()
        #     plt.legend(loc='lower right')
        #     plt.xlabel('Input current [A]')
        #     plt.ylabel('Voltage [V]')
        #     plt.title('Line Regulation during Irradiation')
        #=======================================================================

    def LineReg_Curr_Irradiated(self, mode, *files):
        path = '\Messungen\Line Regulation' + str(mode)
        os.chdir(Plot.dir + path)
        
        file = []
        dirList = os.listdir('.')
        
        for sFile in dirList:
            if sFile.find('.csv') == -1:
                continue
            file.append(sFile)
        file = tuple(file) 
            
            
        label = [None] * len(file)
        filename = [None] * len(file)
        dose = [None] * len(file)    
        for i in range(0, len(file)):
            filename[i] = file[i].split("_")[1]
            dose[i] = filename[i].split(".c")[0]
            label[i] = dose[i]
               
        
        
        self.Create_Axes(0, 1, 3, 2, file, label)
        for i in range(0, len(file)):
            plt.figure(1)
            plt.plot(self.I_in[i], self.V_out1[i], label = label[i])
            plt.grid()
            plt.xlabel("Input current [A]")
            plt.ylabel("Voltage [V]")
            plt.title("Line Regulation during irradiation")
            plt.axis([0,0.7,0,1.3])
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
         
        plt.show()
        
    def LoadReg_Curr_Irradiated(self, mode, *files):
        path = '\Messungen\Line Regulation' + str(mode)
        os.chdir(Plot.dir + path)
        
        file = []
        dirList = os.listdir('.')
        
        for sFile in dirList:
            if sFile.find('.csv') == -1:
                continue
            file.append(sFile)
        file = tuple(file) 
            
            
        label = [None] * len(file)
        filename = [None] * len(file)
        dose = [None] * len(file)    
        for i in range(0, len(file)):
            filename[i] = file[i].split("_")[1]
            dose[i] = filename[i].split(".c")[0]
            label[i] = dose[i]
               
        print label       
        #self.Create_Axes(0, , Vout1, Vout2, file, label)

        plt.show()
        
        
        
    
    def VrefVout(self, pfad, *file):
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Current Supply Mode', 'Voltage Supply Mode']
        color = ['r', 'b']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        print nf
        for i in range(0, nf):
            print os.getcwd()
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    x[i].append(row[0])
                    y[i].append(row[1])
 
            plt.plot(x[i], y[i], color[i], label = label[i])
        plt.legend(loc='lower right')
        plt.xlabel('Reference voltage [V]')
        plt.ylabel('Output voltage [V]')
        plt.title('Vref vs Vout')
        plt.grid()
        plt.axis([0.4,0.66,0.8,1.32])
        plt.tight_layout()
        plt.savefig('VrefVout.pdf')
            
    
    def Lineregulation_CURR(self, Vref, Iin, Vin, Vout, Vout2, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        v = [[] for v in range(0, nf)]
        w = [[] for w in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 600 mV', 'Vref = 500 mV']
        color = ['r', 'b', 'g']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        
        for i in range(0, nf):
            print os.getcwd()
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                next(plots[i], None)
                for row in plots[i]:
                    x[i].append(row[Iin])
                    y[i].append(row[Vout])
                    v[i].append(row[Vin])

        plt.plot(x[0], y[0], color[0], label = 'Iin vs Vout, ' + label[0])
        plt.plot(x[0], v[0], color[1] + '--', label = 'Iin vs Vin' + label[0])
        plt.legend(loc='lower right')
        plt.xlabel('Input current [A]')
        plt.ylabel('Voltage [V]')
        plt.title('Line Regulation, two parallel ShuLDOs')
        plt.grid()
        plt.axis([0,0.95,0,2])
        plt.tight_layout()
        plt.savefig('CMode_LineReg_Vref_500mV.pdf')
        
        
    def Loadregulation_CURR(self, pfad, z, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        v = [[] for v in range(0,nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 500 mV', 'Vref = 600 mV', 'Vref = 660 mV']
        color = ['r', 'b', 'g']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        print csvfile
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        
        for i in range(0, nf):
            print file[i]
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                next(plots[i], None)
                for row in plots[i]:
                    x[i].append(row[3])
                    y[i].append(row[2])
                    v[i].append(row[0])
        
            plt.figure(z)
            plt.plot(x[i], y[i], color[i], label = 'ILoad vs Vout, ' + label[i])
            plt.plot(x[i], v[i], color[i] + '--', label = 'Iload vs Vin, ' + label[i])
            
        plt.legend(loc='best')
        plt.xlabel('Load current [A]')
        plt.ylabel('Output voltage [V]')
        plt.title('Iin = 0.5 A, Iload vs. Vout & Iload vs. Vin')
        plt.grid()
        plt.axis([0,-0.45, 0.6, 1.6])
        plt.savefig('CMode_LoadReg.pdf')
        
        
if __name__ == '__main__':
    plot = Plot(None)
    

    plot.LineReg_Curr_Irradiated('\Current Supply')




    
