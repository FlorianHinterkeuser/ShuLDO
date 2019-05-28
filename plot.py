'''
Created on 26.11.2018
Overview of scanned RD53A chips
@author: Florian
'''
import os
import csv
import logging
from os.path import isfile, join, normpath, normcase
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import Analysis
import math

class Chip_overview(object):

    def plot_iv(self, data = None, chip = '000', flavor = 'IV', specifics = '', filename = "file", fit_length = 50):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax1.axis([0,1.2,0,2.1])

        for key in data.keys():
            datas = data[key]['data']
            iin, vin, vout, vref, voffs = [],[],[],[],[]
        
            logging.info("Plotting averaged values")
            for row in datas:
                iin.append((row[0]))
                vin.append(row[1])
                vout.append(row[2])
                vref.append(row[3])
                voffs.append(row[4])
            
            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='red', label='Input Voltage')
            ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='blue', label='Offset Voltage')
            ax1.plot(iin, vref, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='olive', label='Reference Voltage')
            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='purple', label='Output Voltage')

            x = np.polyfit(iin[-fit_length:], vin[-fit_length:], 1)
            y = np.polyfit(iin[-fit_length:], voffs[-fit_length:], 1)

            u_in = []
            offs = []

            offset_mean = np.mean(voffs[-fit_length:]) * 2
            for i in range(len(iin)):
                u_in.append(iin[i] * x[0] + x[1])
                offs.append(iin[i] * y[0] + y[1])
            self.vin_fits_vdd.append([x[0], x[1]])
            self.voffs_fits_vdd.append([y[0], y[1], offset_mean])


#            ax1.plot(iin, u_in, linestyle='--', linewidth= 0.05, markersize = '.4', color='orange', label = 'Reff from input Voltage fit = %.2f Ohm, offset = %.2f V' % (x[0], x[1]))
#            ax1.plot(iin, offs, linestyle='--', linewidth= 0.05, markersize = '.4', color='cyan', label = 'Offset from measurement = %.2f V, Slope = %.2f V/A' % (offset_mean,y[0]))
        
        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        legend_dict = { 'Input Voltage' : 'red', 'Offset Voltage' : 'blue', 'Reference Voltage' : 'olive', 'Output Voltage' : 'purple'}
        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]
        
        plt.legend(lines, labels, loc = 2)
        plt.grid()
        logging.info("Saving plot %s" % filename)
        try:
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished.")
        plt.close()

    def plot_iv_col2(self, data=None, chip='000', flavor='IV', specifics='', filename="file", fit_length=50):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax1.axis([0, 1.2, 0, 2.1])

        colorsceme = ['red', 'blue', 'green', 'olive', 'purple', 'black']
        colorcount = 0

        for key in data.keys():
            print(key)
            datas = data[key]['data']
            iin, vin, vout, vref, voffs = [], [], [], [], []

            logging.info("Plotting averaged values")
            for row in datas:
                iin.append((row[0]))
                vin.append(row[1])
                vout.append(row[2])
                vref.append(row[3])
                voffs.append(row[4])

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=colorsceme[colorcount],
                         label='Input Voltage')
            ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=colorsceme[colorcount],
                         label='Offset Voltage')
            ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=colorsceme[colorcount],
                         label='Reference Voltage')
            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=colorsceme[colorcount],
                         label='Output Voltage')

            x = np.polyfit(iin[-fit_length:], vin[-fit_length:], 1)
            y = np.polyfit(iin[-fit_length:], voffs[-fit_length:], 1)

            u_in = []
            offs = []

            offset_mean = np.mean(voffs[-fit_length:]) * 2
            for i in range(len(iin)):
                u_in.append(iin[i] * x[0] + x[1])
                offs.append(iin[i] * y[0] + y[1])
            self.vin_fits_vdd.append([x[0], x[1]])
            self.voffs_fits_vdd.append([y[0], y[1], offset_mean])

            #            ax1.plot(iin, u_in, linestyle='--', linewidth= 0.05, markersize = '.4', color='orange', label = 'Reff from input Voltage fit = %.2f Ohm, offset = %.2f V' % (x[0], x[1]))
            #            ax1.plot(iin, offs, linestyle='--', linewidth= 0.05, markersize = '.4', color='cyan', label = 'Offset from measurement = %.2f V, Slope = %.2f V/A' % (offset_mean,y[0]))

        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        legend_dict = {'Input Voltage': 'red', 'Offset Voltage': 'blue', 'Reference Voltage': 'olive',
                           'Output Voltage': 'purple'}
        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()
        logging.info("Saving plot %s" % filename)
        try:
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished.")
        plt.close()

    def plot_iv2(self, data = None, chip = '000', flavor = "IV2", specifics = '', filename = "file", fit_length = 50):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax1.axis([0,1.2,0,2.1])

        for key in data.keys():
            datas = data[key]['data']
            iin, vin, vout, vrefpre, voutpre, vbandgap = [], [], [], [], [], []

            logging.info("Plotting averaged values")
            for row in datas:
                iin.append((row[0]))
                vin.append(row[1])
                vout.append(row[2])
                vrefpre.append(row[3])
                voutpre.append(row[4])
                vbandgap.append(row[5])

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='red', label='Input Voltage')
            ax1.plot(iin, voutpre, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='blue', label='Preregulator Output Voltage')
            ax1.plot(iin, vbandgap, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='green', label='Bandgap Voltage')
            ax1.plot(iin, vrefpre, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='olive', label='Preregulator Reference Voltage')
            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '1', color='purple', label='Output Voltage')


        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")

        legend_dict = { 'Input Voltage' : 'red', 'Prereg Output Voltage' : 'blue', 'Preregulator Reference Voltage' : 'olive', 'Output Voltage' : 'purple', 'Bandgap Voltage' : 'green'}
        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc = 2)
        plt.grid()
        logging.info("Saving plot %s" % filename)
        try:
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics +'.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished.")
        plt.close()

    def plot_currentmirror(self, data = None, chip = '000', specifics = '', filename = "file", fit_length = 50):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.axis([0, 1.2, 0, 2.1])
        ax2.axis([0, 1.2, 0, 1200])

        for key in data.keys():
            datas = data[key]['data']
            iin, vin, vext, current_mirror = [], [], [], []

            for row in datas:
                iin.append((row[0]))
                vin.append(row[1])
                vext.append(row[5])
            for x in range(0, len(vin)):
                rext_current = vext[x] / 817
                current_mirror.append((iin[x] - (rext_current * 2)) / rext_current)

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='red',
                     label='Input Voltage')
            ax1.plot(iin, vext, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='green',
                     label='External Resistor Voltage')
            ax2.plot(iin, current_mirror, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='black',
                     label='Current Mirror')

            x = np.polyfit(iin[-fit_length:], vin[-fit_length:], 1)
            z = np.polyfit(iin, current_mirror[:], 1)
            u_in = []
            mirror_ratio = np.mean(current_mirror)
            for i in range(len(iin)):
                u_in.append(iin[i] * x[0] + x[1])

            self.vin_fits_vdd.append([x[0], x[1]])
            self.mirror.append(mirror_ratio)

            #            ax1.plot(iin, u_in, linestyle='--', linewidth= 0.05, markersize = '.4', color='orange', label = 'Reff from input Voltage fit = %.2f Ohm, offset = %.2f V' % (x[0], x[1]))
            #            ax1.plot(iin, offs, linestyle='--', linewidth= 0.05, markersize = '.4', color='cyan', label = 'Offset from measurement = %.2f V, Slope = %.2f V/A' % (offset_mean,y[0]))
            logging.info("Current Mirror ratio is %s" % mirror_ratio)

        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("Current Mirror Ratio")

        legend_dict = {'Input Voltage': 'red', 'Current Mirror': 'black', 'Rext Voltage': 'green'}
        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()
        logging.info("Saving plot %s" % filename)
        try:
            plt.savefig('Chip' + chip[-3:] + '_CM' + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:] + '_CM' + specifics + '.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished CurrentMirror Plot.")
        plt.close()

    def plot_ntc(self, data = None, chip = '000', specifics = '', filename = "file", fit_length = 50):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax2.axis([0,1.2,0,40])

        ntc1_exists = False
        ntc2_exists = False
        ntc3_exists = False

        for key in data.keys():
            print key
            datas = data[key]['data']
            iin, vin, vext, vout, vref, voffs = [], [], [], [], [], []
            diin, dvin, dvext, dvout, dvref, dvoffs = [], [], [], [], [], []
            diinl, dvinl, dvextl, dvoutl, dvrefl, dvoffsl = [], [], [], [], [], []
            diinh, dvinh, dvexth, dvouth, dvrefh, dvoffsh = [], [], [], [], [], []

            for row in datas:
                iin.append((row[0]))
                diin.append((row[6]))
                vin.append(row[1])
                dvin.append((row[7]))
                vout.append(row[2])
                dvout.append(row[8])
                vref.append(row[3])
                dvref.append(row[9])
                voffs.append(row[4])
                dvoffs.append(row[10])
#                vext.append(1.0/row[5])
                vext.append(1/(1./298.15 + 1./3435. * math.log(row[5]/10000.))-273.15)
            #for i in range(len(dvin)):
            #    dvinl.append(vin[i] - dvin[i])
            #    dvinh.append(vin[i] + dvin[i])
            #    dvextl.append(vext[i]-dvext[i])
            #    dvexth.append(vext[i]+dvext[i])
            #    dvoutl.append(vout[i]-dvout[i])
            #    dvouth.append(vout[i]+dvout[i])
            #    dvrefl.append(vref[i]-dvref[i])
            #    dvrefh.append(vref[i]+dvref[i])
            #    dvoffsl.append(voffs[i]-dvoffs[i])
            #    dvoffsh.append(voffs[i]+dvoffs[i])

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='red',
                     label='Input Voltage')
            #ax1.fill_between(iin, dvinl, dvinh, facecolors='tomato')

            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='purple',
                     label='Output Voltage')
            ax2.plot(iin, vext, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='black',
                     label='NTC')
            if 'NTC1' in key:
                ntc1_exists = True
                ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='blue',
                     label='Offset Voltage')
                ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='olive',
                     label='Reference Voltage')
            elif 'NTC2' in key:
                ntc2_exists = True
                ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='green',
                         label='R_ext Voltage')
                ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='orange',
                         label='Bandgap Voltage')
            elif 'NTC3' in key:
                ntc3_exists = True
                ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='yellow',
                         label='Prereg Reference Voltage')
                ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='brown',
                         label='Prereg Output Voltage')

            #            ax1.plot(iin, u_in, linestyle='--', linewidth= 0.05, markersize = '.4', color='orange', label = 'Reff from input Voltage fit = %.2f Ohm, offset = %.2f V' % (x[0], x[1]))
            #            ax1.plot(iin, offs, linestyle='--', linewidth= 0.05, markersize = '.4', color='cyan', label = 'Offset from measurement = %.2f V, Slope = %.2f V/A' % (offset_mean,y[0]))


        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("NTC Temperature")
        if ntc1_exists and ntc2_exists and ntc3_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'Offset Voltage': 'blue', 'Reference Voltage': 'olive', 'R_ext Voltage': 'green', 'Bandgap': 'orange',
                    'Prereg Reference Voltage': 'yellow', 'Prereg Output Voltage': 'brown'}
        elif ntc1_exists and ntc2_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'Offset Voltage': 'blue', 'Reference Voltage': 'olive', 'R_ext Voltage': 'green', 'Bandgap': 'orange'}
        elif ntc1_exists and ntc3_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'Offset Voltage': 'blue', 'Reference Voltage': 'olive', 'Prereg Reference Voltage': 'yellow', 'Prereg Output Voltage': 'brown'}
        elif ntc2_exists and ntc3_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'R_ext Voltage': 'green', 'Bandgap': 'orange', 'Prereg Reference Voltage': 'yellow', 'Prereg Output Voltage': 'brown'}
        elif ntc1_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'Offset Voltage': 'blue', 'Reference Voltage': 'olive'}
        elif ntc2_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'R_ext Voltage': 'green', 'Bandgap': 'orange'}
        elif ntc3_exists:
            legend_dict = {'Input Voltage': 'red', 'Output Voltage': 'purple', 'NTC': 'black', 'Prereg Reference Voltage': 'yellow', 'Prereg Output Voltage': 'brown'}

        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()
        logging.info("Saving plot %s" % filename)
        try:
            plt.savefig('Chip' + chip[-3:]  + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:]  + specifics + '.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished OVP_ref Plot.")
        plt.close()

    def plot_iv_spread(self, chip = '000', specifics = ''):
        self.vin_effective_res = []
        self.voffs_slope = []
        self.vin_offset = []
        self.voffs_offset = []
        self.voffs_means = []
    
        for item in self.vin_fits_vdd:
            self.vin_effective_res.append(item[0])
            self.vin_offset.append(item[1])
        for item in self.voffs_fits_vdd:
            self.voffs_slope.append(item[0])
            self.voffs_offset.append(item[1]*2)
            self.voffs_means.append(item[2])
        plt.plot(self.scan_parameter, self.vin_effective_res, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='red', label='Effective Input Resistances')
        plt.plot(self.scan_parameter, self.vin_offset, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='blue', label='Offset from Vin')
        plt.plot(self.scan_parameter, self.voffs_offset, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='green', label='Voffs fit offset')
        plt.plot(self.scan_parameter, self.voffs_means, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='black', label='Mean Voffs')
        plt.legend()
        plt.grid()
        plt.axis([-0.1,9,0.5,1.2])
        plt.savefig("Regulator Spread_Chip" + chip[-3:] + specifics + ".pdf")
        plt.close()
        plt.figure()

    def averaging(self, filelist):
        raw_data, rows, cols = [], [], []
        files = len(filelist)
        for file in filelist:
            filecontent = Analysis.file_to_array(file)
            header = filecontent['header']
            data = filecontent['data']
            raw_data.append(data), rows.append(filecontent['rows']), cols.append(filecontent['cols'])
        rows = min(rows)
        cols = min(cols)
            
        data = np.empty(shape=(cols,rows,files))
        interpreted_data_mean = np.empty(shape=(rows, cols))
        interpreted_data_dev = np.empty_like(interpreted_data_mean)
        
        raw_data = np.asarray(raw_data)
        for x in range(0, cols):
            for y in range(0, rows):
                for z in range(0, files):
                    data[x][y][z] = raw_data[z][y][x]
                    
                interpreted_data_mean[y][x] = np.mean(data[x][y])
                interpreted_data_dev[y][x] = np.std(data[x][y])
    #            error = np.mean(data[x][y])*0.0125
    #            interpreted_data_dev[y][x] = np.std(data[x][y]) + error
        interpreted_data = np.array([interpreted_data_mean, interpreted_data_dev])
    

        with open('average.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            spamwriter.writerow(header)
            for row in interpreted_data[0]:
                spamwriter.writerow(row)
        with open('average_dev.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            spamwriter.writerow(header)
            for row in interpreted_data[1]:
                spamwriter.writerow(row)

    def create_iv_overview(self, chip_id, flavor, specifics,  **kwargs):
        self.mirror = []
        os.chdir(normpath(root_path + "/output/" + chip_id + "/" + flavor))
        filelist, self.vin_fits_vdd, self.voffs_fits_vdd, self.scan_parameter = [],  [],  [],  []
        collected_data = {}
        
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                if 'csv' in name and 'BN' in name and specifics in name:
                    filelist.append(name)
        #self.averaging(filelist)
    
        for i, files in enumerate(filelist):
            collected_data[files] = self.file_to_array(files)
            self.scan_parameter.append(i)
        if flavor == 'IV':
            #self.plot_iv(data = collected_data, chip = chip_id, flavor=flavor, specifics = specifics)
            #self.plot_currentmirror(data = collected_data, chip=chip_id, specifics = specifics)
            self.plot_iv3(data = collected_data, chip=chip_id, specifics = specifics)
            #self.plot_iv_spread(chip = chip_id, specifics = specifics)
        elif flavor == 'IV2':
            self.plot_iv2(data=collected_data, chip = chip_id, flavor=flavor, specifics = specifics)

        elif flavor == 'IV_NTC1':
            # self.plot_iv(data = collected_data, chip = chip_id, flavor=flavor, specifics = specifics)
            # self.plot_currentmirror(data = collected_data, chip=chip_id, specifics = specifics)
            self.plot_ntc(data=collected_data, chip=chip_id, specifics=specifics)
            # self.plot_iv_spread(chip = chip_id, specifics = specifics)


    def file_to_array(self, file):
        header = np.genfromtxt(file, dtype=None, delimiter = ',', max_rows = 1)
        data = np.genfromtxt(file, float, delimiter=',', skip_header=1)
        rows = len(data)
        cols = len(data[0])
        return {'header': header, 'data': data, 'rows' : rows, 'cols' : cols}


if __name__ == "__main__":
    root_path = os.getcwd()
    chips = Chip_overview()
    chip_id = 'RD53B_SLDO_BN016'
    flavor = 'IV_NTC1'
    specifics = '_NTC1'
    chips.create_iv_overview(chip_id, flavor, specifics)
#        chips.create_current_mirror_overview(reg_flavor = flavor)