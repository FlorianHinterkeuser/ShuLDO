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
import yaml

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

    def plot_ntc(self, data = None, chip = '000', specifics = '', filename = "file", fit_length = [25, 45]):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        scale2 = [0, 40]
        scalex = 0
        ntc1_exists = False
        ntc2_exists = False
        ntc3_exists = False
        legend_dict = {}

        for key in data.keys():
            save_k = key.split('_')
            save_key = save_k[0]
            self.scan_parameter.append(float(save_key))
            datas = data[key]['data']
            iin, vin, vext, vout, vref, voffs, iref, voutpre = [], [], [], [], [], [], [], []
            diin, dvin, dvext, dvout, dvref, dvoffs, diref, dvoutpre = [], [], [], [], [], [], [], []
            diinl, dvinl, dvextl, dvoutl, dvrefl, dvoffsl = [], [], [], [], [], []
            diinh, dvinh, dvexth, dvouth, dvrefh, dvoffsh = [], [], [], [], [], []

            for row in datas:
                iin.append((row[0]))
                diin.append((row[8]))
                vin.append(row[1])
                dvin.append((row[9]))
                vout.append(row[2])
                dvout.append(row[10])
                vref.append(row[3])
                dvref.append(row[11])
                voffs.append(row[4])
                dvoffs.append(row[12])
                iref.append(row[5])
                diref.append(row[13])
                voutpre.append(row[6])
                dvoutpre.append(row[14])
#                vext.append(1.0/row[5])
                vext.append(1/(1./298.15 + 1./3435. * math.log(row[7]/10000.))-273.15)
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
            legend_dict['Input Voltage'] = 'red'
            ax1.fill_between(iin, dvinl, dvinh, facecolors='tomato')

            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='purple',
                     label='Output Voltage')
            legend_dict['Output Voltage'] = 'purple'
            ax2.plot(iin, vext, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='black',
                     label='NTC')
            legend_dict['NTC'] = 'black'

            min_ntc = min(vext) - 5
            max_ntc = max(vext) + 5
            if scale2[0] > min_ntc:
                scale2[0] = min_ntc
            if scale2[1] < max_ntc:
                scale2[1] = max_ntc


            max_x = max(iin) + 0.05
            if scalex < max_x:
                scalex = max_x
            #if 'NTC1' in key:
            ntc1_exists = True
            ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='blue',
                 label='Offset Voltage')
            legend_dict['Offset Voltage'] = 'blue'
            ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='olive',
                 label='Reference Voltage')
            legend_dict['Reference Voltage'] = 'olive'
            #elif 'NTC2' in key:
            #    ntc2_exists = True
            #    ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='green',
            #             label='R_ext Voltage')
            #    legend_dict['R_ext Voltage'] = 'green'
            #    ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='orange',
            #             label='Bandgap Voltage')
            #    legend_dict['Bandgap Voltage'] = 'orange'
            #elif 'NTC3' in key:
            ntc3_exists = True
            ax1.plot(iin, voutpre, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='yellow',
                     label='Prereg Output Voltage')
            legend_dict['Prereg Output Voltage'] = 'yellow'
            ax1.plot(iin, iref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='brown',
                     label='Reference Current')
            legend_dict['Reference Current Sense'] = 'brown'

            #Fits to determine R_eff and Offs
            x = np.polyfit(iin[fit_length[0]:fit_length[1]], vin[fit_length[0]:fit_length[1]], 1)
            y = np.polyfit(iin[fit_length[0]:fit_length[1]], voffs[fit_length[0]:fit_length[1]], 1)

            self.fit_to_data(iin, vout, save_key, 'V_out', fit_length)
            self.fit_to_data(iin, voutpre, save_key, 'V_outpre', fit_length)
            self.fit_to_data(iin, iref, save_key, 'I_ref', fit_length)
            self.fit_to_data(iin, vref, save_key, 'V_ref', fit_length)
            #u_in = []
            #offs = []

            offset_mean = np.mean(voffs[fit_length[0]:])

            #for i in range(len(iin)):
            #    u_in.append(iin[i] * x[0] + x[1])
            #    offs.append(iin[i] * y[0] + y[1])
            self.vin_fits_vdd.append([x[0], x[1]])
            self.voffs_fits_vdd.append([y[0], y[1], offset_mean])
            try:
                self.fit_log[flavor]
            except:
                self.fit_log[flavor] = {}

            try:
                self.fit_log[flavor]["run" + save_key]
            except:
                self.fit_log[flavor]["run" + save_key] = {}

            try:
                self.fit_log[flavor]["run" + save_key]["Offs"]
            except:
                self.fit_log[flavor]["run" + save_key]["Offs"] = {}

            self.fit_log[flavor]["run" + save_key]["R_eff"] = float(x[0])
            self.fit_log[flavor]["run" + save_key]["Offs"]["eff"] = float(x[1])
            self.fit_log[flavor]["run" + save_key]["Offs"]["mean"] = float(offset_mean)
            self.fit_log[flavor]["run" + save_key]["Offs"]["offset"] = float(y[1])
            self.fit_log[flavor]["run" + save_key]["Offs"]["slope"] = float(y[0])

        ax2.axis([0.1, scalex, scale2[0], scale2[1]])

        if flavor == 'LoadReg':
            ax1.set_xlabel("Load Current / A")
        else:
            ax1.set_xlabel("Input Current / A")

        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("NTC Temperature")

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
        logging.info("Finished OVP_ref Plot.")
        plt.close()

    def plot_iv_spread(self, chip = '000', specifics = ''):
        self.vin_effective_res = []
        self.voffs_slope = []
        self.vin_offset = []
        self.voffs_offset = []
        self.voffs_means = []
        temps = [30, 15, 0, -15, -30, -40]
        y_axis = []
    
        for item in self.vin_fits_vdd:
            self.vin_effective_res.append(item[0])
            self.vin_offset.append(item[1])
        for item in self.voffs_fits_vdd:
            self.voffs_slope.append(item[0])
            self.voffs_offset.append(item[1])
            self.voffs_means.append(item[2])

        for i in range(len(self.scan_parameter)):
            y_axis.append(self.dose[int(self.scan_parameter[i])])

        order = np.argsort(y_axis)
        vin_effective_res_s = np.array(self.vin_effective_res)[order]
        vin_offset_s = np.array(self.vin_offset)[order]
        voffs_offset_s = np.array(self.voffs_offset)[order]
        voffs_mean_s = np.array(self.voffs_means)[order]
        scan_parameter_s = np.array(y_axis)[order]

        plt.semilogx(scan_parameter_s, vin_effective_res_s, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='red', label='Effective Input Resistances')
        plt.semilogx(scan_parameter_s, vin_offset_s, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='blue', label='Offset from Vin')
        plt.semilogx(scan_parameter_s, voffs_offset_s, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='green', label='Voffs fit offset')
        plt.semilogx(scan_parameter_s, voffs_mean_s, linestyle='-', marker='.', linewidth= 0.3, markersize = '3', color='black', label='Mean Voffs')
        plt.legend()
        plt.grid()
        plt.axis([min(y_axis)-5,max(y_axis)+5,0.5,1.2])
        plt.savefig("Regulator Spread_Chip" + chip[-3:] +"_"+ flavor + specifics + ".pdf")
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

    def file_to_array(self, file):
        header = np.genfromtxt(file, dtype=None, delimiter = ',', max_rows = 1)
        data = np.genfromtxt(file, float, delimiter=',', skip_header=1)
        rows = len(data)
        cols = len(data[0])
        return {'header': header, 'data': data, 'rows' : rows, 'cols' : cols}

    def dump_plotdata(self):
        log = open(self.name, 'w+')
        yaml.dump(self.fit_log, log)
        log.close()

    def create_fit_log(self, chip_id):
        self.name = "Chip_" + chip_id[-3:] + "_fit_log.yaml"
        if os.path.isfile(self.name):
            log = open(self.name, 'r')
            self.fit_log = yaml.load(log)
            log.close()
        else:
            self.fit_log = {}

    def fit_to_data(self, x, y, save_key, name, fit_length):
        fit_res = np.polyfit(x[fit_length[0]:], y[fit_length[0]:], 1)
        fit_mean = np.mean(y[fit_length[0]:])

        try:
            self.fit_log[flavor]
        except:
            self.fit_log[flavor] = {}

        try:
            self.fit_log[flavor]["run" + save_key]
        except:
            self.fit_log[flavor]["run" + save_key] = {}

        try:
            self.fit_log[flavor]["run" + save_key][name]
        except:
            self.fit_log[flavor]["run" + save_key][name] = {}

        self.fit_log[flavor]["run" + save_key][name]["mean"] = float(fit_mean)
        self.fit_log[flavor]["run" + save_key][name]["offset"] = float(fit_res[1])
        self.fit_log[flavor]["run" + save_key][name]["slope"] = float(fit_res[0])

    def plot_from_fit_log(self, ax1, ax2, scale1, scale2, scale_x, name):
        fit_log = yaml.load(open(self.name, 'r'))
        p_slope, p_mean, p_offs, x_axis, x_axis_c = [], [], [], [], []

        for runs in fit_log[flavor]:
            runs_save = runs[3:]
            x_axis.append(int(runs_save))
            p_slope.append(fit_log[flavor][runs][name]['slope'])
            p_mean.append(fit_log[flavor][runs][name]['mean'])
            p_offs.append(fit_log[flavor][runs][name]['offset'])

        order = np.argsort(x_axis)
        p_slope_s = np.array(p_slope)[order]
        p_mean_s = np.array(p_mean)[order]
        p_offs_s = np.array(p_offs)[order]
        x_axis_s = np.array(x_axis)[order]

        for i in range(len(self.scan_parameter)):
            x_axis_c.append(self.dose[int(x_axis_s[i])])

        label1 = str(name + ' slope')
        label2 = str(name + ' mean')
        label3 = str(name + ' offset')
        color1 = 'red'
        color2 = 'green'
        color3 = 'blue'
        ax1.semilogx(x_axis_c, p_slope_s, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=color1, label=label1)
        self.legend_dict[label1] = color1
        ax2.semilogx(x_axis_c, p_mean_s, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=color2, label=label2)
        self.legend_dict[label2] = color2
        ax2.semilogx(x_axis_c, p_offs_s, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=color3, label=label3)
        self.legend_dict[label3] = color3

        new_min = (min(p_slope) - 0.01)
        if new_min < scale1[0]:
            scale1[0] = new_min

        new_max = (max(p_slope) + 0.01)
        if new_max > scale1[1]:
            scale1[1] = new_max

        new_min = (min(p_offs) - min(p_offs) * 0.1)
        if new_min < scale2[0]:
            scale2[0] = new_min

        new_max = (max(p_offs) + max(p_offs) * 0.1)
        if new_max > scale2[1]:
            scale2[1] = new_max

        new_min = (min(p_mean) - min(p_mean) * 0.1)
        if new_min < scale2[0]:
            scale2[0] = new_min

        new_max = (max(p_mean) + max(p_mean) * 0.1)
        if new_max > scale2[1]:
            scale2[1] = new_max

        new_min = (float(min(x_axis_c)) - float(min(x_axis_c)) * 0.1)
        if new_min < scale2[0]:
            scale_x[0] = new_min

        new_max = (float(max(x_axis_c)) + float(max(x_axis_c)) * 0.1)
        if new_max > scale2[1]:
            scale_x[1] = new_max

    def create_plot(self, name, chip_id):
        try:
            self.name
        except:
            self.name = "Chip_" + chip_id[-3:] + "_fit_log.yaml"

        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        scale_x = [1.0, 2.0]
        scale1 = [0.1, 0.01]
        scale2 = [0.5, 0.]
        self.legend_dict = {}

        self.plot_from_fit_log(ax1, ax2, scale1, scale2, scale_x, name)

        ax1.set_xlabel(flavor2 + ' / Mrad')
        ax1.set_ylabel("Slope Voltage  / V/Mrad")
        ax2.set_ylabel("Voltage / V")
        ax1.axis([scale_x[0], scale_x[1], scale1[0], scale1[1]])
        ax2.axis([scale_x[0], scale_x[1], scale2[0], scale2[1]])

        colors = self.legend_dict.values()
        labels = self.legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()
        plt.savefig(chip_id + "_"+ flavor + "_Fit_" + name +".pdf")
        plt.close()

    def create_iv_overview(self, chip_id, flavor, specifics, main=False, **kwargs):
        self.mirror = []
        root_path = os.getcwd()

        if main:
            if flavor2 is 'TID':
                os.chdir(normpath(root_path + "/Xray/" + chip_id + "/" + flavor2))
                self.dose = [0, 0.1, 0.2, 1., 2., 3., 5., 10., 20., 50., 100., 200., 300., 400., 500., 600.]
            else:
                os.chdir(normpath(root_path + "/output/" + chip_id + "/" + flavor))
        else:
            print('plotting')

        filelist, self.vin_fits_vdd, self.voffs_fits_vdd, self.scan_parameter = [], [], [], []
        collected_data = {}
        self.create_fit_log(chip_id)

        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                if 'csv' in name and specifics in name and flavor in name:
                    filelist.append(name)
        # self.averaging(filelist)

        for i, files in enumerate(filelist):
            collected_data[files] = self.file_to_array(files)
            # self.scan_parameter.append(i)
        if flavor == 'IV':
            # self.plot_iv(data = collected_data, chip = chip_id, flavor=flavor, specifics = specifics)
            # self.plot_currentmirror(data = collected_data, chip=chip_id, specifics = specifics)
            self.plot_iv(data=collected_data, chip=chip_id, specifics=specifics)
            # self.plot_iv_spread(chip = chip_id, specifics = specifics)
        elif flavor == 'IV2':
            self.plot_iv2(data=collected_data, chip=chip_id, flavor=flavor, specifics=specifics)

        elif 'LoadReg' in flavor:
            self.plot_ntc(data=collected_data, chip=chip_id, specifics=specifics, fit_length=[0, 15])
            self.dump_plotdata()
            self.create_plot('V_out', chip_id)
            self.create_plot('V_outpre', chip_id)
            self.create_plot('V_ref', chip_id)
            self.create_plot('I_ref', chip_id)
            self.create_plot('Offs', chip_id)

        else:
            #self.plot_iv(data = collected_data, chip = chip_id, flavor=flavor, specifics = specifics)
            #self.plot_currentmirror(data = collected_data, chip=chip_id, specifics = specifics)
            self.plot_ntc(data=collected_data, chip=chip_id, specifics=specifics)
            self.dump_plotdata()
            self.plot_iv_spread(chip=chip_id, specifics=specifics)
            self.create_plot('V_out', chip_id)
            self.create_plot('V_outpre', chip_id)
            self.create_plot('V_ref', chip_id)
            self.create_plot('I_ref', chip_id)

if __name__ == "__main__":
    root_path = os.getcwd()
    chips = Chip_overview()
    chip_id = 'BN004'
    flavor2 = 'TID'
    flavor = 'LoadReg'
    specifics = ''
    chips.create_iv_overview(chip_id, flavor, specifics, main=True)
#        chips.create_current_mirror_overview(reg_flavor = flavor)