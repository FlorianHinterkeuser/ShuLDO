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
import math
import yaml
from matplotlib.pyplot import cm
import matplotlib.colors as mplcolor
from matplotlib.collections import LineCollection

class Chip_overview(object):
    def plot_iv_col(self, filelist, name='V_in', data=None, chip='000', flavor='IV', specifics='', filename="file", log = True):
        scalex = 0.6
        iin_a = []
        varr = []
        doses = []

        for key in filelist:
            save_k = key.split('_')
            save_key = save_k[0]
            save_key = int(save_key)
            if save_key == 0 and log:
                continue
            doses.append(self.dose[save_key])

            datas = data[key]['data']
            iin, vin = [], []

            for row in datas:
                iin.append((row[0]))
                vin.append(row[self.list_of_names[name]['loc']])

            max_x = max(iin) + 0.05
            if scalex < max_x:
                scalex = max_x

            iin_a.append(np.array(iin))
            varr.append(np.array(vin))


        iin = np.array(iin_a)
        vin = np.array(varr)
        dose = np.array(doses)

        for i in range(2):
            fig, ax = plt.subplots()

            if i == 0:
                lc = self.multiline(iin, vin, dose, norm=mplcolor.LogNorm(vmin=dose.min(), vmax=dose.max()), cmap='viridis', lw=0.15)
            else:
                lc = self.multiline(iin, vin, dose, cmap='viridis', lw=0.15)
            axcb = fig.colorbar(lc)

            if flavor == 'LoadReg':
                ax.set_title('Load Regulation: ' + self.list_of_names[name]['title'])
                ax.set_xlabel("Load Current / A")
            else:
                ax.set_xlabel("Input Current / A")
                ax.set_title('Line Regulation: ' + self.list_of_names[name]['title'])

            ax.axis([0, scalex, 0, 2.1])
            ax.set_ylabel("Voltage / V")
            axcb.set_label("TID / MRad")

            plt.grid()
            logging.info("Saving plot %s" % filename)
            filepath = self.filepath + '/' + flavor + '/Colored'
            if not os.path.exists(os.path.normpath(filepath)):
                os.makedirs(os.path.normpath(filepath))
            os.chdir(normpath(filepath))
            try:
                if i == 0:
                    plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '_' + name + '_Colored_log.pdf')
                else:
                    plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '_' + name + '_Colored.pdf')
            except:
                logging.error("Plot %s could not be saved" % filename)
                raise ValueError
            logging.info("Finished.")
            os.chdir(normpath(self.filepath))
            plt.close()


    def plot_iv_col2(self, filelist, name='V_in', data=None, chip='000', flavor='IV', specifics='', filename="file"):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        scalex = 0.6

        legend_dict = {}
        color = iter(cm.rainbow(np.linspace(0, 1, len(data.keys()))))

        for key in filelist:
            c = next(color)

            save_k = key.split('_')
            save_key = save_k[0]
            save_key = int(save_key)

            datas = data[key]['data']
            iin, vin = [], []


            for row in datas:
                iin.append((row[0]))
                vin.append(row[self.list_of_names[name]['loc']])

            label = name + ' (' + str(self.dose[save_key]) + 'Mrad)'

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color=c,
                         label=label)

            legend_dict[label] = c

            max_x = max(iin) + 0.05
            if scalex < max_x:
                scalex = max_x

        if flavor == 'LoadReg':
            ax1.set_xlabel("Load Current / A")
        else:
            ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("Dose / MRad")

        ax1.axis([0, scalex, 0, 2.1])

        cax = plt.axes([0.85, 0.1, 0.075, 0.8])
        fig.colorbar(cax=cax)

        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()

        logging.info("Saving plot %s" % filename)
        filepath = self.filepath + '/' + flavor +'/Colored'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))
        try:
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '_' + name + '_Colored.pdf')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished.")
        os.chdir(normpath(self.filepath))

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
            diinl, dvinl, dvextl, dvoutl, dvrefl, dvoffsl, direfl, dvoutprel = [], [], [], [], [], [], [], []
            diinh, dvinh, dvexth, dvouth, dvrefh, dvoffsh, direfh, dvoutpreh = [], [], [], [], [], [], [], []

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
            if specifics != '':
                for i in range(len(dvin)):
                    dvinl.append(vin[i] - dvin[i])
                    dvinh.append(vin[i] + dvin[i])

                    dvoutl.append(vout[i]-dvout[i])
                    dvouth.append(vout[i]+dvout[i])

                    dvrefl.append(vref[i]-dvref[i])
                    dvrefh.append(vref[i]+dvref[i])

                    dvoffsl.append(voffs[i]-dvoffs[i])
                    dvoffsh.append(voffs[i]+dvoffs[i])

                    direfl.append(voffs[i] - diref[i])
                    direfh.append(voffs[i] + diref[i])

                    dvoutprel.append(voutpre[i] - dvoutpre[i])
                    dvoutpreh.append(voutpre[i] + dvoutpre[i])

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='red',
                     label='Input Voltage')
            legend_dict['Input Voltage'] = 'red'
            if specifics != '':
                ax1.fill_between(iin, dvinl, dvinh, facecolors='tomato')

            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='purple',
                     label='Output Voltage')
            legend_dict['Output Voltage'] = 'purple'
            if specifics != '':
                ax1.fill_between(iin, dvoutl, dvouth, facecolors='magenta')

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
            if specifics != '':
                ax1.fill_between(iin, dvoffsl, dvoffsh, facecolors='lightblue')

            ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='olive',
                 label='Reference Voltage')
            legend_dict['Reference Voltage'] = 'olive'
            if specifics != '':
                ax1.fill_between(iin, dvrefl, dvrefh, facecolors='yellowgreen')
            #elif 'NTC2' in key:
            #    ntc2_exists = True
            #    ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='green',
            #             label='R_ext Voltage')
            #    legend_dict['R_ext Voltage'] = 'green'
            #    if specifics != '':
            #       ax1.fill_between(iin, dvoffsl, dvoffsh, facecolors='lightgreen')
            #
            #    ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='orange',
            #             label='Bandgap Voltage')
            #    legend_dict['Bandgap Voltage'] = 'orange'
            #    if specifics != '':
            #       ax1.fill_between(iin, dvrefl, dvrefh, facecolors='navajowhite')
            #
            #elif 'NTC3' in key:
            ntc3_exists = True
            ax1.plot(iin, voutpre, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='yellow',
                     label='Prereg Output Voltage')
            legend_dict['Prereg Output Voltage'] = 'yellow'
            if specifics != '':
                ax1.fill_between(iin, dvoutprel, dvoutpreh, facecolors='lightyellow')

            ax1.plot(iin, iref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='brown',
                     label='Reference Current')
            legend_dict['Reference Current Sense'] = 'brown'
            if specifics != '':
                ax1.fill_between(iin, direfl, direfh, facecolors='indianred')

            #Fits to determine R_eff and Offs
            x = np.polyfit(iin[fit_length[0]:fit_length[1]], vin[fit_length[0]:fit_length[1]], 1)
            y = np.polyfit(iin[fit_length[0]:fit_length[1]], voffs[fit_length[0]:fit_length[1]], 1)

            self.fit_to_data(iin, vout, save_key, 'V_out', fit_length)
            self.fit_to_data(iin, voutpre, save_key, 'V_outpre', fit_length)
            self.fit_to_data(iin, iref, save_key, 'I_ref', fit_length)
            self.fit_to_data(iin, vref, save_key, 'V_ref', fit_length)

            offset_mean = np.mean(voffs[fit_length[0]:])

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
        filepath = self.filepath + '/' + flavor
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))
        try:
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.pdf')
            plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '.png')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished IV Plot.")
        os.chdir(normpath(self.filepath))
        plt.close()

    def plot_iv_spread(self, chip = '000', specifics = ''):
        fit_log = yaml.load(open(self.name, 'r'))
        self.vin_effective_res = []
        self.voffs_slope = []
        self.vin_offset = []
        self.voffs_offset = []
        self.voffs_means = []
        temps = [30, 15, 0, -15, -30, -40]
        y_axis = []
        x_axis_c = []
        x_err = []

        for runs in fit_log[flavor]:
            runs_save = runs[3:]
            y_axis.append(int(runs_save))
            self.vin_effective_res.append(fit_log[flavor][runs]['R_eff'])
            self.voffs_slope.append(fit_log[flavor][runs]['Offs']['slope'])
            self.vin_offset.append(fit_log[flavor][runs]['Offs']['eff'])
            self.voffs_offset.append(fit_log[flavor][runs]['Offs']['offset'])
            self.voffs_means.append(fit_log[flavor][runs]['Offs']['mean'])

        order = np.argsort(y_axis)
        vin_effective_res_s = np.array(self.vin_effective_res)[order]
        vin_offset_s = np.array(self.vin_offset)[order]
        voffs_offset_s = np.array(self.voffs_offset)[order]
        voffs_mean_s = np.array(self.voffs_means)[order]
        x_axis_s = np.array(y_axis)[order]

        for i in range(len(x_axis_s)):
            x_axis_c.append(self.dose[int(x_axis_s[i])])
            x_err.append(self.dose[int(x_axis_s[i])]*0.2)

        plt.errorbar(x_axis_c, vin_effective_res_s, None, x_err, marker='.', fmt='o', linewidth= 0.3, markersize = '3', color='red', capsize= 2, markeredgewidth=1, label='Effective Input Resistances')
        plt.errorbar(x_axis_c, vin_offset_s, None, x_err,  marker='.', fmt='o', linewidth= 0.3, markersize = '3', color='blue', capsize= 2, markeredgewidth=1, label='Offset from Vin')
        plt.errorbar(x_axis_c, voffs_offset_s, None, x_err, marker='.', fmt='o', linewidth= 0.3, markersize = '3', color='green', capsize= 2, markeredgewidth=1, label='Voffs fit offset')
        plt.errorbar(x_axis_c, voffs_mean_s, None, x_err, marker='.', fmt='o', linewidth= 0.3, markersize = '3', color='black', capsize= 2, markeredgewidth=1, label='Mean Voffs')
        plt.semilogx()

        plt.legend()
        plt.grid()
        plt.axis([min(x_axis_c)-min(x_axis_c)*0.25, max(x_axis_c)+max(x_axis_c)*0.25, 0.5, 1.2])

        filepath = self.filepath + '/' + flavor + '/Fits'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))
        plt.savefig("Regulator Spread_Chip" + chip[-3:] +"_"+ flavor + specifics + ".pdf")
        os.chdir(normpath(self.filepath))

        plt.close()
        plt.figure()

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
        if flavor == 'LoadReg':
            fit_res = np.polyfit(x[fit_length[0]:fit_length[1]], y[fit_length[0]:fit_length[1]], 1)
            fit_mean = np.mean(y[fit_length[0]:fit_length[1]])
        else:
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
        x_err = []

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

        for i in range(len(x_axis_s)):
            x_axis_c.append(self.dose[int(x_axis_s[i])])
            x_err.append(self.dose[int(x_axis_s[i])]*0.2)

        label1 = str('slope')
        label2 = str('mean')
        label3 = str('offset')
        color1 = 'red'
        color2 = 'green'
        color3 = 'blue'
        ax1.errorbar(x_axis_c, p_slope_s, None, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color1, capsize= 2, markeredgewidth=1, label=label1)
        ax1.semilogx()
        self.legend_dict[label1] = color1
        ax2.errorbar(x_axis_c, p_mean_s, None, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color2, capsize= 2, markeredgewidth=1, label=label2)
        self.legend_dict[label2] = color2
        ax2.errorbar(x_axis_c, p_offs_s, None, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color3, capsize= 2, markeredgewidth=1, label=label3)
        ax2.semilogx()
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

        if flavor == 'LoadReg':
            ax1.set_title('Fit to Load Regulation: ' + self.list_of_names[name]['title'])
        else:
            ax1.set_title('Fit to Line Regulation: ' + self.list_of_names[name]['title'])

        ax1.set_xlabel(flavor2 + ' / Mrad')
        ax1.set_ylabel("Slope Voltage  / V/A")
        ax2.set_ylabel("Voltage / V")
        ax1.axis([scale_x[0], scale_x[1], scale1[0], scale1[1]])
        ax2.axis([scale_x[0], scale_x[1], scale2[0], scale2[1]])

        colors = self.legend_dict.values()
        labels = self.legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        plt.grid()

        filepath = self.filepath + '/' + flavor + '/Fits'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))

        plt.savefig(chip_id + "_" + flavor + "_Fit_" + name +".pdf")

        os.chdir(normpath(self.filepath))

        plt.close()

    def sort_filelist(self, filelist):
        fl = []
        for file in filelist:
            save_k = file.split('_')
            save_key = save_k[0]
            fl.append(int(save_key))
        order = np.argsort(fl)

        for i in range(len(order)):
            fl[i] = filelist[order[i]]

        return fl

    def multiline(self, xs, ys, c, ax=None, **kwargs):
        # from https://stackoverflow.com/questions/38208700/matplotlib-plot-lines-with-colors-through-colormap; Alex Williams; 24.04.2018
        """Plot lines with different colorings

        Parameters
        ----------
        xs : iterable container of x coordinates
        ys : iterable container of y coordinates
        c : iterable container of numbers mapped to colormap
        ax (optional): Axes to plot on.
        kwargs (optional): passed to LineCollection

        Notes:
            len(xs) == len(ys) == len(c) is the number of line segments
            len(xs[i]) == len(ys[i]) is the number of points for each line (indexed by i)

        Returns
        -------
        lc : LineCollection instance.
        """

        # find axes
        ax = plt.gca() if ax is None else ax

        # create LineCollection
        segments = [np.column_stack([x, y]) for x, y in zip(xs, ys)]
        lc = LineCollection(segments, **kwargs)

        # set coloring of line segments
        #    Note: I get an error if I pass c as a list here... not sure why.
        lc.set_array(np.asarray(c))

        # add lines to axes and rescale
        #    Note: adding a collection doesn't autoscalee xlim/ylim
        ax.add_collection(lc)
        ax.autoscale()
        return lc

    def create_iv_overview(self, chip_id, flavor, specifics, main=False, **kwargs):
        self.mirror = []
        root_path = os.getcwd()
        if main:
            if flavor2 is 'TID':
                self.filepath = root_path + "/Xray/" + chip_id + "/" + flavor2
                os.chdir(normpath(self.filepath))
                self.dose = [0, 0.1, 0.2, 0.5, 1., 2., 3., 5., 10., 20., 50., 100., 200., 300., 400., 500., 600., 700., 800.]
            else:
                self.filepath = root_path + "/output/" + chip_id + "/" + flavor2
                os.chdir(normpath(self.filepath))
        else:
            self.filepath = root_path
            print('plotting')

        filelist, self.vin_fits_vdd, self.voffs_fits_vdd, self.scan_parameter = [], [], [], []
        collected_data = {}
        self.create_fit_log(chip_id)

        self.list_of_names = {'V_in': {'loc': 1, 'title': 'Input Voltage'},
                              'V_out': {'loc': 2, 'title': 'Output Voltage'},
                              'V_ref': {'loc': 3, 'title': 'Reference Voltage'},
                              'V_offs': {'loc': 4, 'title': 'Offset Voltage'},
                              'I_ref': {'loc': 5, 'title': 'Reference Current Sense Voltage'},
                              'V_outpre': {'loc': 6, 'title': 'Preregulator Output Voltage'},
                              'NTC': {'loc': 7, 'title': 'NTC Temperature'},
                              'Offs': {'title': 'Offset Voltage'}}

        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                if 'csv' in name and specifics in name and flavor in name:
                    filelist.append(name)
        # self.averaging(filelist)
        filelist = self.sort_filelist(filelist)

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

            self.plot_iv_col(filelist, name='V_in', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_out', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_ref', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_offs', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='I_ref', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_outpre', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)


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

            self.plot_iv_col(filelist, name='V_in', data=collected_data, chip=chip_id, flavor=flavor, specifics=specifics)
            self.plot_iv_col(filelist, name='V_out', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_ref', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_offs', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='I_ref', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)
            self.plot_iv_col(filelist, name='V_outpre', data=collected_data, chip=chip_id, flavor=flavor,
                              specifics=specifics)

if __name__ == "__main__":
    root_path = os.getcwd()
    chips = Chip_overview()
    chip_id = 'BN004'
    flavor2 = 'TID'
    flavor = 'LineReg'
    specifics = ''
    chips.create_iv_overview(chip_id, flavor, specifics, main=True)
#        chips.create_current_mirror_overview(reg_flavor = flavor)