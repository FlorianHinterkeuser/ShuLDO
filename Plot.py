'''

@author: Wilhelm Linac
'''

import time
import logging
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
import os.path
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib import _cm_listed as cmap
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset


class Plot(object):
    
    dir = os.getcwd()
    
    def __init__(self, nf):
        self.V_in = []
        self.V_out1 = []
        self.V_out2 = []
        self.I_in = []
        self.I_load1 = []
        self.result = []
        self.nf = nf
        self.plasma = cmap._inferno_data
    
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
        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
            
        for i in range(0,nf):
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                header = next(plots[i]) 
                
                for row in plots[i]:
                    csvfilearray[i].append(row)
                    if 'Regulator 2 output voltage [V]' in header and 'Regulator 1 load current [A]' in header:
                        Iload1 = 0
                        Vout2 = 1
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.v[i].append(row[Iload1])
                        self.w[i].append(row[Vout2])
                    elif 'Regulator 1 load current [A]' in header and 'Regulator 2 output voltage [V]' not in header:
                        Iload1 = 3
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.v[i].append(row[Iload1])
                    elif 'Regulator 1 load current [A]' not in header and 'Regulator 2 output voltage [V]' in header:
                        Vout2 = 2
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                        self.w[i].append(row[Vout2])                    
                    elif 'Regulator 1 load current [A]' not in header and 'Regulator 2 output voltage [V]' not in header:
                        self.x[i].append(row[Vin])
                        self.y[i].append(row[Iin])
                        self.z[i].append(row[Vout1])
                    else:
                        raise RuntimeError('Error occured')
        for i in range(0, nf):
            pass
        self.result = [self.x, self.y, self.z, self.v, self.w]
        return self.result
        
    def Create_Axes(self, Vin, Iin, Vout1, file):
        
        self.Readout(Vin, Iin, Vout1, file)                                     #L2C Issue
        self.V_in = self.result[0]
        self.I_in = self.result[1]
        self.V_out1 = self.result[2]
        self.I_load1 = self.result[3]
        self.V_out2 = self.result[4]
        self.color = [None]*len(file)        
        
        Output1 = self.V_out1
        for i in range(0, len(file)):
            for j in range(0, len(self.V_out1[i])):
                if float(self.V_out1[i][j]) > 1000:
                    self.V_out1[i][j] = float(self.V_out1[i][j])/1000
                    if float(self.V_out1[i][j]) < 1:
                        raise RuntimeError
        
        for i in range(0, len(file)):
            self.scale = int(len(self.plasma)/len(file))*i
            self.color[i] = self.plasma[self.scale]          


    def LineReg_Curr_Irradiated(self, mode):
        path = '\Messungen\Line Regulation' + str(mode)
        os.chdir(Plot.dir + path)
        file = []
        dirList = os.listdir('.')

        for sFile in dirList:
            if sFile.find('.csv') == -1:
                continue
            file.append(sFile)
        file = tuple(file) 
        
        self.Create_Axes(Vin = 0, Iin = 1, Vout1 = 3, file=file)
        
        for i in range(0, len(file)):
            fig1 = plt.figure(1)
            ax1=fig1
            plt.plot(self.I_in[i], self.V_out2[i], color = self.color[i], alpha=0.8)
            plt.grid(True)
            plt.xlabel("Input Current [A]")
            plt.ylabel("Regulator 2 Output Voltage [V]")
            plt.title("Iin vs. Vout2")
            plt.axis([0.,0.7,0.,1.25])
            
            fig2 = plt.figure(2)
            ax2=fig2
            plt.plot(self.I_in[i], self.V_out1[i], color = self.color[i], alpha=0.8)
            plt.grid(True)
            plt.xlabel("Input current [A]")
            plt.ylabel("Regulator 1 output voltage [V]")
            plt.title("Iin vs. Vout1")
            plt.axis([0,0.7,0,1.25])
            
            fig3 = plt.figure(3)
            ax3=fig3
            plt.plot(self.I_in[i], self.V_in[i], color = self.color[i], alpha=0.8)
            plt.grid(True)
            plt.xlabel("Input current [A]")
            plt.ylabel("Input voltage [V]")
            plt.title("Iin vs. Vin")
            plt.axis([0,0.7,0,1.9])
            
        sm = plt.cm.ScalarMappable(cmap = 'plasma', norm = plt.Normalize(vmin=0, vmax=500))
        sm._A = []
        cbar1= fig1.colorbar(sm)
        cbar1.set_label('Total Dose [Mrad]', rotation = 270, labelpad=20)
        cbar2=fig2.colorbar(sm)
        cbar2.set_label('Total Dose [Mrad]', rotation = 270, labelpad = 20)
        cbar3=fig3.colorbar(sm)        
        cbar3.set_label('Total Dose [Mrad]', rotation = 270, labelpad = 20)
        
        ax1 = fig1.add_subplot(111)                                                     #Setting up subplots for zooming
        ax2 = fig2.add_subplot(111)
        
        axins1 = zoomed_inset_axes(ax1, 2, bbox_to_anchor=(267,167))
        axins2 = zoomed_inset_axes(ax2, 2, bbox_to_anchor=(307,167))
        
        axins1.grid(False)
        axins2.grid(False)
        axins1.set_xlim(0.35,0.45)
        axins2.set_xlim(0.4,0.5)
        axins1.set_ylim(1.13, 1.24)
        axins2.set_ylim(1.13,1.24)
        
        for i in range(0, len(file)):
            axins1.plot(self.I_in[i], self.V_out2[i], color = self.color[i], alpha=0.8)
            axins2.plot(self.I_in[i], self.V_out1[i], color = self.color[i], alpha=0.8)
        mark_inset(ax1, axins1, 2,1, fc="none", ec= "0")
        mark_inset(ax2, axins2, 2, 1, fc="none", ec="0")
                
        plt.figure(1).savefig("IinVout2.pdf")
        plt.figure(2).savefig("IinVout1.pdf")
        plt.figure(3).savefig("InVin.pdf")
        plt.close('all')
        
    def LineReg_live(self, file_name):
        print "Pass!"
        pass
        
    def LoadReg_Curr_Irradiated(self, mode, *files):
        path = '\Messungen\Load Regulation' + str(mode)
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
        
        self.Create_Axes(Vin = 3, Iin= 4, Vout1= 5, file = file)
        
        for i in range(0, len(file)):            
            
            fig1 = plt.figure(1)
            plt.plot(self.I_load1[i], self.V_out2[i], label = label[i], alpha=0.8, color = self.color[i])
            plt.xlabel('Load current [A]')
            plt.ylabel("Voltage [V]")
            plt.grid(True)
            plt.title("Vout2 vs. Iload")
            plt.axis([0,0.42,1.19,1.205]) 
                   
            fig2 = plt.figure(2)
            plt.plot(self.I_load1[i], self.V_out1[i], label = label[i], alpha=0.8, color = self.color[i])
            plt.xlabel('Load current [A]')
            plt.ylabel("Voltage [V]")
            plt.grid(True)
            plt.title("Vout1 vs. Iload")
            plt.axis([0,0.42,1.16,1.21])
             
            fig3 = plt.figure(3)
            plt.plot(self.I_load1[i], self.V_in[i], label = label[i], alpha=0.8, color = self.color[i])
            plt.xlabel('Load current [A]')
            plt.ylabel("Voltage [V]")
            plt.grid(True)
            plt.title("Vin vs. Iload")
            plt.axis([0,0.42,1.3,1.5])
        sm = plt.cm.ScalarMappable(cmap = 'plasma', norm = plt.Normalize(vmin=0, vmax=500))
        sm._A = []
        cbar1= fig1.colorbar(sm)
        cbar1.set_label('Total Dose [Mrad]', rotation = 270, labelpad = 20)
        cbar2=fig2.colorbar(sm)
        cbar2.set_label('Total Dose [Mrad]', rotation = 270, labelpad = 20)
        cbar3=fig3.colorbar(sm)        
        cbar3.set_label('Total Dose [Mrad]', rotation = 270, labelpad = 20)
        
        plt.figure(1).savefig("IloadvsVout2.pdf")
        plt.figure(2).savefig("IloadvsVout1.pdf")
        plt.figure(3).savefig("IloadvsVin.pdf")
        #plt.show()
        plt.close('all')

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
        
    def LivePlot(self, file_name):
        #plot.LineReg_live(file_name)   
        #print os.getcwd()
        file = []
        header = []
        csvfilearray = []
        
        dirList = os.listdir('.')
        for sFile in dirList:
            if sFile.find('.csv') == -1:
                continue
            file.append(sFile)
        file = tuple(file)   
        print file
        
        with open(file_name, 'rb') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            header = next(plots)
            for row in plots:
                csvfilearray.append(row)

        
        for i in range(0, len(header)):
            if "Input voltage" in header[i]:
                self.Vin = i
                logging.info("Input voltage in column %r" % i)
            elif "output voltage" in header[i] and "1" in header[i]:                    #Beware: lower case "o" in output voltage!
                self.Vout1 = i
                logging.info("Output voltage 1 in column %r" % i)
            elif "output voltage" in header[i] and "2" in header[i]:
                self.Vout2 = i
                logging.info("Output voltage 2 in column %r" % i)
            elif "load current" in header[i]:
                self.Iload1 = i
                logging.info("Load current in column %r" % i)
            elif "Input current" in header[i]:
                self.Iin = i
                logging.info("Input current in column %r" % i)
                
        self.V_in = [None]*len(csvfilearray) 
        self.I_in = [None]*len(csvfilearray) 
        self.V_out1 = [None]*len(csvfilearray) 
        self.V_out2 = [None]*len(csvfilearray) 
        self.I_load1 = [None]*len(csvfilearray) 
        load = [None] * len(csvfilearray)
        
        
        for i in range(0, len(csvfilearray)):
            try:
                self.V_in[i] = csvfilearray[i][self.Vin]
                self.I_in[i] = csvfilearray[i][self.Iin]
                self.V_out1[i] = csvfilearray[i][self.Vout1]
                self.V_out2[i] = csvfilearray[i][self.Vout2]
                self.I_load1[i] = csvfilearray[i][self.Iload1]
            except AttributeError:
                pass
        

        
        if "line" in file_name or "Line" in file_name:
            fig1=plt.figure(1)
            plt.grid(True)
            plt.plot(self.I_in, self.V_out1, color = self.plasma[100])
            plt.xlabel("Input Current [A]")
            plt.ylabel("Regulator 1 Output Voltage [V]")
            
            fig2 = plt.figure(2)
            plt.grid(True)
            plt.plot(self.I_in, self.V_in, color = self.plasma[100])
            plt.xlabel("Input Current [A]")
            plt.ylabel("Regulator 2 Output Voltage [V]")
            plt.show()
            
            pass
        elif "load" in file_name or "Load" in file_name:
            fig1=plt.figure(1)
            plt.grid(True)
            plt.plot(self.I_load1, self.V_out1, color = self.plasma[100])
            plt.xlabel("Load Current [A]")
            plt.ylabel("Regulator 1 Output Voltage [V]")
            plt.xlim(float(self.I_load1[0]), float(self.I_load1[-1]))
            
            fig2=plt.figure(2)
            plt.grid(True)
            plt.plot(self.I_load1, self.V_out2, color = self.plasma[100])
            plt.xlabel("Load Current [A]")
            plt.ylabel("Regulator 2 Output Voltage [V]")
            plt.xlim(float(self.I_load1[0]), float(self.I_load1[-1]))
            
            fig3=plt.figure(3)
            plt.grid(True)
            plt.plot(self.I_load1, self.V_in, color = self.plasma[100])
            plt.xlabel("Load Current [A]")
            plt.ylabel("Input Voltage [V]")
            plt.xlim(float(self.I_load1[0]), float(self.I_load1[-1]))
            
            plt.show()
            plt.close("all")

    def DoseVoltage(self, mode, Last, eingang):
        path = '\Messungen\\' + str(mode) + '\Current Supply'
        os.chdir(Plot.dir + path)
        file = []
        dirList = os.listdir('.')
                
        for sFile in dirList:
            if sFile.find('.csv') == -1:
                continue
            file.append(sFile)
            
        file = tuple(file)    
        dose = [None] * len(file) ; label= [None] * len(file) ; filename= [None] * len(file) 
        header, csvfilearray, Iload, Vin, TotDose, Vout1, Vout2, Iin = [],[],[],[],[],[],[],[]
        
        for i in range(0, len(file)):
            filename[i] = file[i].split("_")[1]
            dose[i] = filename[i].split("Mrad")[0]
            label[i] = dose[i]

        for i in range(0, len(file)):
            csvfilearray = []
            with open(file[i], 'rb') as csvfile:
                plot = csv.reader(csvfile, delimiter=',')
                header = next(plot)
                for row in plot:
                    csvfilearray.append(row)
            for j in range(0,len(header)):
                if "load" in header[j] and "set" in header[j]:
                    load = j
                    print 1
                if "out" in header[j] and "1" in header[j]:
                    out1 = j
                    print 2
                if "out" in header[j] and "2" in header[j]:
                    out2 = j
                    print 3
                if "In" in header[j] and "[V]" in header[j]:
                    vinput = j
                    print 4
                if "In" in header[j] and "current" in header[j]:
                    iinput = j
                    print 5
            
            print "Line" in file[i]
            
            if "Load" in file[i]:
                for column in csvfilearray:
                    if str(Last) in column[load]:
                        Iload.append(column[load])
                        TotDose.append(dose[i])
                        Vout1.append(column[out1])
                        Vout2.append(column[out2])
                        Vin.append(column[vinput])
            if "Line" in file[i]:
                for column in csvfilearray:
                    if str(eingang) in column[iinput]:
                        Vin.append(column[vinput])
                        Vout1.append(column[out1])
                        Vout2.append(column[out2])
                        TotDose.append(dose[i])
        try:
            plt.plot(dose, Vout1)
            plt.plot(dose, Vout2)
            plt.plot(dose, Vin)
            plt.grid(True)
            plt.show()
        except NameError:
            pass

        
if __name__ == '__main__':
    plot = Plot(None)
    
    #plot.LineReg_Curr_Irradiated('\Current Supply')
    #plot.LoadReg_Curr_Irradiated('\Current Supply')
    #plot.LivePlot('CMode_600_500_mV_LoadReg.csv')
    plot.DoseVoltage('Line Regulation', 0.21, 0.46)
    plot.DoseVoltage('Load Regulation', 0.21, 0.46)
    
