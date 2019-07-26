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
from scipy.odr import odrpack as odr
from scipy.odr import models

class Chip_overview(object):
    def plot_ntc(self, data=None, chip='000', specifics='', filename="file", fit_length=[25, 45]):
        fig = plt.figure(1, figsize=(8, 4.8))
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
                if row[0] > 1.2:
                    break
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
                vext.append(1 / (1. / 298.15 + 1. / 3435. * math.log(row[7] / 10000.)) - 273.15)
            if specifics != '':
                for i in range(len(dvin)):
                    dvinl.append(vin[i] - vin[i]*0.001 - 0.01)
                    dvinh.append(vin[i] + vin[i]*0.001 + 0.01)

                    dvoutl.append(vout[i] - dvout[i])
                    dvouth.append(vout[i] + dvout[i])

                    dvrefl.append(vref[i] - dvref[i])
                    dvrefh.append(vref[i] + dvref[i])

                    dvoffsl.append(voffs[i] - dvoffs[i])
                    dvoffsh.append(voffs[i] + dvoffs[i])

                    direfl.append(voffs[i] - diref[i])
                    direfh.append(voffs[i] + diref[i])

                    dvoutprel.append(voutpre[i] - dvoutpre[i])
                    dvoutpreh.append(voutpre[i] + dvoutpre[i])

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='red',
                     label='Input Voltage')
            legend_dict['V_in'] = 'red'
            if specifics != '':
                ax1.fill_between(iin, dvinl, dvinh, facecolors='tomato')

            ax1.plot(iin, vout, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='purple',
                     label='V_out')
            legend_dict['V_out'] = 'purple'
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

            # if 'NTC1' in key:
            ntc1_exists = True
            ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='blue',
                     label='Offset Voltage')
            legend_dict['V_offs'] = 'blue'
            if specifics != '':
                ax1.fill_between(iin, dvoffsl, dvoffsh, facecolors='lightblue')

            ax1.plot(iin, vref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='olive',
                     label='Reference Voltage')
            legend_dict['V_ref'] = 'olive'
            if specifics != '':
                ax1.fill_between(iin, dvrefl, dvrefh, facecolors='yellowgreen')
            # elif 'NTC2' in key:
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
            # elif 'NTC3' in key:
            ntc3_exists = True
            ax1.plot(iin, voutpre, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='orange',
                     label='Prereg Output Voltage')
            legend_dict['V_outpre'] = 'orange'
            if specifics != '':
                ax1.fill_between(iin, dvoutprel, dvoutpreh, facecolors='navajowhite')

            ax1.plot(iin, iref, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='brown',
                     label='Reference Current')
            if flavor2 == 'IV_NTC1':
                legend_dict['V_refpre'] = 'brown'
                fit_length = [76, 199]
            else:
                legend_dict['I_ref Sense'] = 'brown'
            if specifics != '':
                ax1.fill_between(iin, direfl, direfh, facecolors='indianred')

            # Fits to determine R_eff and Offs
            x, x_err = self.poly_lsq(iin[fit_length[0]:fit_length[1]], vin[fit_length[0]:fit_length[1]], 1)

            y, y_err = self.poly_lsq(iin[fit_length[0]:fit_length[1]], voffs[fit_length[0]:fit_length[1]], 1)

            self.fit_to_data(iin, vout, save_key, 'V_out', fit_length)
            self.fit_to_data(iin, voutpre, save_key, 'V_outpre', fit_length)
            self.fit_to_data(iin, iref, save_key, 'I_ref', fit_length)
            self.fit_to_data(iin, vref, save_key, 'V_ref', fit_length)

            offset_mean = np.mean(voffs[fit_length[0]:])
            offset_mean_err = np.std(voffs[fit_length[0]:])

            try:
                self.fit_log[flavor]
            except:
                self.fit_log[flavor] = {}

            try:
                self.fit_log[flavor]["run" + save_key]
            except:
                self.fit_log[flavor]["run" + save_key] = {}

            try:
                self.fit_log[flavor]["run" + save_key]["V_offs"]
            except:
                self.fit_log[flavor]["run" + save_key]["V_offs"] = {}

            self.fit_log[flavor]["run" + save_key]["R_eff"] = [float(x[0]), float(x_err[0])]
            self.fit_log[flavor]["run" + save_key]["V_offs"]["eff"] = [float(x[1]), float(x_err[1])]
            self.fit_log[flavor]["run" + save_key]["V_offs"]["mean"] = [float(offset_mean), float(offset_mean_err)]
            self.fit_log[flavor]["run" + save_key]["V_offs"]["offset"] = [float(y[1]), float(y_err[1])]
            self.fit_log[flavor]["run" + save_key]["V_offs"]["slope"] = [float(y[0]), float(y_err[0])]

        ax2.axis([0, scalex, scale2[0], scale2[1]])
        ax1.axis([0, scalex, 0, 2.1])

        if flavor == 'LoadReg':
            ax1.set_xlabel("Load Current / A")
            ax1.set_title("IV-Overview: Load Regulation")
        else:
            ax1.set_xlabel("Input Current / A")
            ax1.set_title("IV-Overview: Line Regulation")

        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("NTC Temperature")

        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, bbox_to_anchor=(1.05, 1.0),loc=2, fontsize='small')
        plt.grid()
        plt.tight_layout()

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


    def plot_iv_col(self, filelist, name='V_in', data=None, chip='000', flavor='IV', specifics='', filename="file", log = False):
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
            if flavor2 == 'TID':
                doses.append(self.dose[save_key])
            elif flavor2 == 'Temperatur':
                doses.append(self.temp[save_key])

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


        fig, ax = plt.subplots()

        if log:
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
        if flavor2 == 'TID':
            axcb.set_label("TID / MRad")
        elif flavor2 == 'Temperatur':
            axcb.set_label("Temperature / *C")

        plt.grid()
        logging.info("Saving plot %s" % filename)
        filepath = self.filepath + '/' + flavor + '/Colored'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))
        try:
            if log:
                plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '_' + name + '_Colored_log.pdf')
            else:
                plt.savefig('Chip' + chip[-3:] + '_' + flavor + specifics + '_' + name + '_Colored.pdf')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
        logging.info("Finished.")
        os.chdir(normpath(self.filepath))
        plt.close()


    def plot_iv_poly(self, filelist, name='V_in', data=None, chip='000', flavor='IV', filename="file"):
        try:
            self.name
        except:
            self.name = "Chip_" + chip_id[-3:] + "_fit_log.yaml"
        fit_log = yaml.load(open(self.name, 'r'))

        for key in filelist:
            save_k = key.split('_')
            save_key = save_k[0]


            datas = data[key]['data']
            iin, vin = [], []
            p, x = [0., 0.], [0., 0.]
            scalex = 0.6

            fig = plt.figure(1)
            ax1 = fig.add_subplot(111)

            for row in datas:
                iin.append((row[0]))
                vin.append(row[self.list_of_names[name]['loc']])

            if name == 'V_in' and flavor == 'LineReg':
                p[0] = (fit_log[flavor]['run' + str(save_key)]['R_eff'])[0]
                p[1] = (fit_log[flavor]['run' + str(save_key)]['V_offs']['eff'])[0]
            else:
                p[0] = (fit_log[flavor]['run' + str(save_key)][name]['slope'])[0]
                p[1] = (fit_log[flavor]['run' + str(save_key)][name]['offset'])[0]

            if flavor2 == 'TID':
                label = self.list_of_names[name]['title'] + ' (' + str(self.dose[int(save_key)]) + 'Mrad)'
            elif flavor2 == 'Temperatur':
                label = self.list_of_names[name]['title'] + ' (' + str(self.temp[int(save_key)]) + '*C)'
            else:
                label = self.list_of_names[name]['title']

            ax1.plot(iin, vin, linestyle='-', marker='.', linewidth=0.5, markersize='1', label='Data')

            max_x = max(iin) + 0.05
            if scalex < max_x:
                scalex = max_x

            x[1] = scalex
            y = np.polyval(p, x)
            ax1.plot(x, y, linestyle='-', marker=None, linewidth=0.5, label='Fit')

            ax1.set_title(label)
            if flavor == 'LoadReg':
                ax1.set_xlabel("Load Current / A")
            else:
                ax1.set_xlabel("Input Current / A")
            ax1.set_ylabel("Voltage / V")


            ax1.axis([0, scalex, 0, 2.1])

            plt.legend()
            plt.grid()

            logging.info("Saving plot %s" % filename)
            filepath = self.filepath + '/' + flavor + '/Fits/Polyval/run' + str(save_key)
            if not os.path.exists(os.path.normpath(filepath)):
                os.makedirs(os.path.normpath(filepath))
            os.chdir(normpath(filepath))
            try:
                plt.savefig('Chip' + chip[-3:] + '_' + flavor + '_' + str(save_key) + '_' + name + '.pdf')
            except:
                logging.error("Plot %s could not be saved" % filename)
                raise ValueError
            logging.info("Finished.")
            os.chdir(normpath(self.filepath))

            plt.close()


    def analysis_currentmirror(self, data = None, chip = '000', specifics = '', filename = "file", fit_length = 50, measure_iext=True):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.axis([0, 1.2, 0, 2.1])
        ax2.axis([0, 1.2, 0, 1200])

        fit_ranges = {'800': [6, 25], '700': [9, 28], '600': [9, 33], '500': [13, 38]}

        for key in data.keys():
            save_k = key.split('_')
            save_key = float(save_k[0])
            datas = data[key]['data']
            iin, vin, vext, iext = [], [], [], []
            diin, dvin, dvext, diext = [], [], [], []
            for row in datas:
                iin.append((row[0]))
                diin.append(row[5])
                vin.append(row[1])
                dvin.append(row[6])
                vext.append(row[2])
                dvext.append(row[7])
                iext.append(row[3])
                diext.append(row[8])

            iin_s = np.array(iin)
            diin_s = np.array(diin)
            vin_s = np.array(vin)
            dvin_s = np.array(dvin)
            vext_s = np.array(vext)
            dvext_s = np.array(dvext)
            iext_s = np.array(iext)
            diext_s = np.array(diext)

            if measure_iext:
                cm_i = (iin_s - 2*iext_s)/iext_s
                dcm_i = np.sqrt((diin_s/iext_s)**2 + ((iin_s*diext_s)/(iext_s**2))**2)

            cm_v = (iin_s*save_key - 2*vext_s)/vext_s
            dcm_v = np.sqrt((diin_s*save_key/vext_s)**2 + ((iin_s*save_key*dvext_s)/(vext_s**2))**2 + (iin_s*0.3/vext_s)**2)

            ax1.plot(iin_s, vin_s, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='red',
                     label='Input Voltage')
            ax1.fill_between(iin_s, vin_s - dvin_s, vin_s + dvin_s, facecolors='tomato')

            ax1.plot(iin_s, vext_s, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='green',
                     label='External Resistor Voltage')
            ax1.fill_between(iin_s, vext_s - dvext_s, vext_s + dvext_s, facecolors='lightgreen')

            if measure_iext:
                ax1.plot(iin_s, iext_s*800, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='blue', label='External Resistor Current')
                ax1.fill_between(iin_s, iext_s*800 - diext_s*800, iext_s*800 + diext_s*800, facecolors='lightblue')
                ax2.plot(iin_s, cm_i, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='black', label='Current Mirror')
                ax2.fill_between(iin_s, cm_i - dcm_i, cm_i + dcm_i, facecolors='gray')


            ax2.plot(iin_s, cm_v, linestyle='-', marker='.', linewidth=0.1, markersize='1', color='purple',
                     label='Current Mirror')
            ax2.fill_between(iin_s, cm_v - dcm_v, cm_v + dcm_v, facecolors='magenta')

            self.fit_to_data(iin_s, vin_s, str(save_key),'V_in', fit_ranges[save_k[0]], cm=True)
            self.fit_to_data(vext_s, iin_s, str(save_key), 'CM_V', fit_ranges[save_k[0]], cm=True)
            self.fit_to_data(iext_s, iin_s, str(save_key), 'CM_I', fit_ranges[save_k[0]], cm=True)

        reff = []
        rext = []

        for runs in self.fit_log[flavor]:
            runs_save = runs[3:]
            try:
                rext.append(float(runs_save))
            except:
                logging.info('Skipped %s' % runs)
                continue
            reff.append(self.fit_log[flavor][runs]['V_in']['slope'][0])
        self.fit_to_data(reff, rext, 'Analysis', 'CM_R', [0, len(reff)])

        ax1.set_xlabel("Input Current / A")
        ax1.set_ylabel("Voltage / V")
        ax2.set_ylabel("Current Mirror Ratio")

        legend_dict = {'Input Voltage': 'red', 'Current Mirror from Iext': 'black', 'Current Mirror from Vext': 'purple', 'Rext Voltage': 'green', 'Iext*800 Ohm': 'blue'}
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

    def plot_currentmirror(self, data = None, chip = '000', specifics = '', filename = "file", fit_length = 50, measure_iext=True):
        fit_log = yaml.load(open(self.name, 'r'))
        x, x_W, CM_I, CM_V, CM_IW, CM_VW = [], [], [], [], [], []
        dCM_I, dCM_V, dCM_IW, dCM_VW = [], [], [], []
        R_eff = []
        dR_eff= []

        for runs in fit_log[flavor]:
            try:
                runs_save = runs[3:]
                x.append(float(runs_save))
            except:
                print('skipped entry')
                continue

            CM_I.append(fit_log[flavor][runs]['CM_I']['slope'][0])
            dCM_I.append(fit_log[flavor][runs]['CM_I']['slope'][1])
            CM_V.append(fit_log[flavor][runs]['CM_V']['slope'][0])
            dCM_V.append(fit_log[flavor][runs]['CM_V']['slope'][1])
            R_eff.append(fit_log[flavor][runs]['V_in']['slope'][0])
            dR_eff.append(fit_log[flavor][runs]['V_in']['slope'][1])

        for key in data.keys():
            save_k = key.split('_')
            save_key = float(save_k[0])
            datas = data[key]['data']

            vext = datas[25][2]
            dvext = datas[25][7]
            iext = datas[25][3]
            diext = datas[25][8]

            cm_i = (0.5 - 2 * iext) / iext
            dcm_i = np.sqrt((datas[25][5] / iext) ** 2 + ((0.5 * diext) / (iext ** 2)) ** 2)

            cm_v = (0.5 * save_key - 2 * vext) / vext
            dcm_v = np.sqrt((datas[25][5] * save_key / vext) ** 2 + ((0.5 * save_key * dvext) / (vext ** 2)) ** 2 + (0.5 * 0.3 / vext) ** 2)
            x_W.append(save_key)
            CM_IW.append(cm_i)
            dCM_IW.append(dcm_i)
            CM_VW.append(cm_v)
            dCM_VW.append(dcm_v)

        order = np.argsort(x)
        CM_Is = np.array(CM_I)[order]
        dCM_Is = np.array(dCM_I)[order]
        CM_Vs = np.array(CM_V)[order]
        dCM_Vs = np.array(dCM_V)[order]
        R_effs = np.array(R_eff)[order]
        dR_effs = np.array(dR_eff)[order]
        xs = np.array(x)[order]

        order = np.argsort(x_W)
        CM_VWs = np.array(CM_VW)[order]
        dCM_VWs = np.array(dCM_VW)[order]
        CM_IWs = np.array(CM_IW)[order]
        dCM_IWs = np.array(dCM_IW)[order]
        x_Ws = np.array(x_W)[order]

        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)

        legend_dict = {}

        ax1.errorbar(xs, CM_Vs, dCM_Vs, 0.3, marker='.', fmt='o', linewidth=0.3,
                     markersize='3', color='blue', capsize=2, markeredgewidth=1, label='Offset from Vin')
        legend_dict['from V_ext'] = 'blue'

        ax1.errorbar(xs, CM_Is, dCM_Is, 0.3, marker='.', fmt='o', linewidth=0.3,
                     markersize='3', color='green', capsize=2, markeredgewidth=1, label='Voffs fit offset')
        legend_dict['from I_ext'] = 'green'

        ax1.errorbar(xs, xs/R_effs, xs*dR_effs/(R_effs*R_effs), 0.3, marker='.', fmt='o', linewidth=0.3,
                     markersize='3', color='black', capsize=2, markeredgewidth=1, label='Mean Voffs')
        legend_dict['R_ext/R_eff'] = 'black'

        ax1.errorbar(x_Ws, CM_IWs, dCM_IWs, 0.3, marker='.', fmt='o', linewidth=0.3,
                     markersize='3', color='olive', capsize=2, markeredgewidth=1, label='Mean Voffs')
        legend_dict['from I_ext at Working Point I_in = 0.6A'] = 'olive'

        ax1.errorbar(x_Ws, CM_VWs, dCM_VWs, 0.3, marker='.', fmt='o', linewidth=0.3,
                     markersize='3', color='purple', capsize=2, markeredgewidth=1, label='Mean Voffs')
        legend_dict['from V_ext at Working Point I_in = 0.6A'] = 'purple'

        ax1.set_xlabel("R_ext / Ohm")
        ax1.set_ylabel("Current Mirror Factor k")

        ax1.set_title('Current Mirror')

        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=3)
        plt.grid()
        plt.tight_layout()

        filepath = self.filepath
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))

        plt.savefig("CurrentMirror" + chip[-3:] + "_" + flavor + ".pdf")

        os.chdir(normpath(self.filepath))

        plt.close()
        plt.figure()

    def plot_iv_spread(self, chip='000', specifics='', rel=False):
        fit_log = yaml.load(open(self.name, 'r'))
        self.vin_effective_res = []
        self.voffs_slope = []
        self.vin_offset = []
        self.voffs_offset = []
        self.voffs_means = []
        self.vin_effective_res_err = []
        self.voffs_slope_err = []
        self.vin_offset_err = []
        self.voffs_offset_err = []
        self.voffs_means_err = []

        temps = [30, 15, 0, -15, -30, -40]
        y_axis = []
        x_axis_c = []
        x_err = []

        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()

        legend_dict = {}

        for runs in fit_log[flavor]:
            runs_save = runs[3:]
            y_axis.append(int(runs_save))

            self.vin_effective_res.append(fit_log[flavor][runs]['R_eff'][0])
            self.voffs_slope.append(fit_log[flavor][runs]['V_offs']['slope'][0])
            self.vin_offset.append(fit_log[flavor][runs]['V_offs']['eff'][0])
            self.voffs_offset.append(fit_log[flavor][runs]['V_offs']['offset'][0])
            self.voffs_means.append(fit_log[flavor][runs]['V_offs']['mean'][0])

            self.vin_effective_res_err.append(fit_log[flavor][runs]['R_eff'][1])
            self.voffs_slope_err.append(fit_log[flavor][runs]['V_offs']['slope'][1])
            self.vin_offset_err.append(fit_log[flavor][runs]['V_offs']['eff'][1])
            self.voffs_offset_err.append(fit_log[flavor][runs]['V_offs']['offset'][1])
            self.voffs_means_err.append(fit_log[flavor][runs]['V_offs']['mean'][1])

        order = np.argsort(y_axis)
        vin_effective_res_s = np.array(self.vin_effective_res)[order]
        vin_offset_s = np.array(self.vin_offset)[order]
        voffs_offset_s = np.array(self.voffs_offset)[order]
        voffs_mean_s = np.array(self.voffs_means)[order]
        x_axis_s = np.array(y_axis)[order]

        vin_effective_res_err_s = np.array(self.vin_effective_res_err)[order]
        vin_offset_err_s = np.array(self.vin_offset_err)[order]
        voffs_offset_err_s = np.array(self.voffs_offset_err)[order]
        voffs_mean_err_s = np.array(self.voffs_means_err)[order]

        for i in range(len(x_axis_s)):
            if flavor2 == 'TID':
                x_axis_c.append(self.dose[int(x_axis_s[i])])
                x_err.append(self.dose[int(x_axis_s[i])]*0.2)
            elif flavor2 == 'Temperatur':
                x_axis_c.append(self.temp[int(x_axis_s[i])])
                x_err.append(1)

        if rel:
            vin_effective_res_s = vin_effective_res_s / vin_effective_res_s[0]
            vin_offset_s = vin_offset_s / vin_offset_s[0]
            voffs_offset_s = voffs_offset_s / voffs_offset_s[0]
            voffs_mean_s = voffs_mean_s / voffs_mean_s[0]

        ax2.errorbar(x_axis_c, vin_effective_res_s, vin_effective_res_err_s, x_err, marker='.', fmt='o', linewidth=0.3, markersize='3', color='red', capsize=2, markeredgewidth=1, label='Effective Input Resistance')
        legend_dict['Effective Input Resistance'] = 'red'
        ax1.errorbar(x_axis_c, vin_offset_s, vin_offset_err_s, x_err,  marker='.', fmt='o', linewidth=0.3, markersize='3', color='blue', capsize=2, markeredgewidth=1, label='Offset from Vin')
        legend_dict['Effective Offset from Fit to V_in'] = 'blue'
        ax1.errorbar(x_axis_c, voffs_offset_s, voffs_offset_err_s, x_err, marker='.', fmt='o', linewidth=0.3, markersize='3', color='green', capsize=2, markeredgewidth=1, label='Voffs fit offset')
        legend_dict['Offset from Fit to V_offs'] = 'green'
        ax1.errorbar(x_axis_c, voffs_mean_s, voffs_mean_err_s, x_err, marker='.', fmt='o', linewidth=0.3, markersize='3', color='black', capsize=2, markeredgewidth=1, label='Mean Voffs')
        legend_dict['Mean Offset Voltage'] = 'black'
        if flavor2 == 'TID':
            ax1.semilogx()

        if not rel:
            ax2.axhline(0.8, color='orange')
            legend_dict['expected effective Resistance'] = 'orange'

        if rel:
            ax1.axis([min(x_axis_c)-min(x_axis_c)*0.25, max(x_axis_c)+max(x_axis_c)*0.25, 0.9, 1.1])
            ax2.axis([min(x_axis_c) - min(x_axis_c) * 0.25, max(x_axis_c) + max(x_axis_c) * 0.25, 0.9, 1.1])
        else:
            ax1.axis([min(x_axis_c)- np.sqrt(min(x_axis_c)**2) * 0.25, max(x_axis_c)+max(x_axis_c)*0.25, 0.4, 1.1])
            ax2.axis([min(x_axis_c) - np.sqrt(min(x_axis_c)**2) * 0.25, max(x_axis_c) + max(x_axis_c) * 0.25, 0.5, 1.2])

        if flavor2 == 'TID':
            ax1.set_xlabel("TID / Mrad")
        elif flavor2 == 'Temperatur':
            ax1.set_xlabel("Fridge Temperature / *C")

        if rel:
            ax1.set_ylabel("Voltage / Voltage(0)")
            ax2.set_ylabel("Resistance / Resistance(0)")

            ax1.set_title('Relative offset changes and effective resistance')
        else:
            ax1.set_ylabel("Voltage / V")
            ax2.set_ylabel("Resistance / Ohm")

            ax1.set_title('Fits to Offset and effective Resistance')

        colors = legend_dict.values()
        labels = legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=3)
        ax1.grid()
        plt.tight_layout()

        filepath = self.filepath + '/' + flavor + '/Fits'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))
        if rel:
            plt.savefig("Relative_Regulator_Spread_Chip" + chip[-3:] + "_" + flavor + ".pdf")
        else:
            plt.savefig("Regulator Spread_Chip" + chip[-3:] + "_" + flavor + ".pdf")
        os.chdir(normpath(self.filepath))

        plt.close()
        plt.figure()


    def create_plot(self, name, chip_id):
        try:
            self.name
        except:
            self.name = "Chip_" + chip_id[-3:] + "_fit_log.yaml"

        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        scale_x = [1.0, 2.0]
        scale2 = [0.1, 0.01]
        scale1 = [0.5, 0.]
        self.legend_dict = {}

        self.plot_from_fit_log(ax2, ax1, scale2, scale1, scale_x, name)

        if flavor == 'LoadReg':
            ax1.set_title('Fit to Load Regulation: ' + self.list_of_names[name]['title'])
        else:
            ax1.set_title('Fit to Line Regulation: ' + self.list_of_names[name]['title'])

        if flavor2 == 'TID':
            ax1.set_xlabel(flavor2 + ' / Mrad')
        elif flavor2 == 'Temperatur':
            ax1.set_xlabel('Fridge' + flavor2 + ' / *C')

        ax2.set_ylabel("Slope  / V/A")
        ax1.set_ylabel("Voltage / V")
        ax1.axis([scale_x[0], scale_x[1], scale1[0], scale1[1]])
        ax2.axis([scale_x[0], scale_x[1], scale2[0], scale2[1]])

        colors = self.legend_dict.values()
        labels = self.legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        ax1.grid()
        plt.tight_layout()

        filepath = self.filepath + '/' + flavor + '/Fits'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))

        plt.savefig(chip_id + "_" + flavor + "_Fit_" + name +".pdf")

        os.chdir(normpath(self.filepath))

        plt.close()


    def create_plot_rel(self, name, chip_id):
        try:
            self.name
        except:
            self.name = "Chip_" + chip_id[-3:] + "_fit_log.yaml"

        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        scale_x = [1.0, 2.0]
        scale1 = [1., 1.]
        scale2 = [0.5, 0.]

        self.legend_dict = {}

        self.plot_from_fit_log(ax2, ax1, scale2, scale1, scale_x, name, rel=True)

        if flavor == 'LoadReg':
                ax1.set_title('Relative Fit to Load Regulation: ' + self.list_of_names[name]['title'])
        else:
                ax1.set_title('Relative Fit to Line Regulation: ' + self.list_of_names[name]['title'])

        if flavor2 == 'TID':
            ax1.set_xlabel(flavor2 + ' / Mrad')
        elif flavor2 == 'Temperatur':
            ax1.set_xlabel(flavor2 + ' / *C')

        ax1.set_ylabel("V/V(0)")
        ax2.set_ylabel("Slope / V/A")
        ax1.axis([scale_x[0], scale_x[1], scale1[0], scale1[1]])
        ax2.axis([scale_x[0], scale_x[1], scale2[0], scale2[1]])

        colors = self.legend_dict.values()
        labels = self.legend_dict.keys()
        lines = [Line2D([0], [0], color=c, linewidth=1, linestyle='-') for c in colors]

        plt.legend(lines, labels, loc=2)
        ax1.grid()
        plt.tight_layout()

        filepath = self.filepath + '/' + flavor + '/Fits'
        if not os.path.exists(os.path.normpath(filepath)):
            os.makedirs(os.path.normpath(filepath))
        os.chdir(normpath(filepath))

        plt.savefig(chip_id + "_" + flavor + "_Fit_relative_" + name +".pdf")

        os.chdir(normpath(self.filepath))

        plt.close()


    def plot_from_fit_log(self, ax1, ax2, scale1, scale2, scale_x, name, rel = False, cm=False):
        fit_log = yaml.load(open(self.name, 'r'))
        p_slope, p_mean, p_offs, x_axis, x_axis_c = [], [], [], [], []
        p_slope_err, p_mean_err, p_offs_err = [], [], []
        x_err = []

        for runs in fit_log[flavor]:
            runs_save = runs[3:]
            try:
                x_axis.append(int(runs_save))
            except:
                logging.info('skipped %s' % runs)
                continue
            p_slope.append(fit_log[flavor][runs][name]['slope'][0])
            p_mean.append(fit_log[flavor][runs][name]['mean'][0])
            p_offs.append(fit_log[flavor][runs][name]['offset'][0])
            p_slope_err.append(fit_log[flavor][runs][name]['slope'][1])
            p_mean_err.append(fit_log[flavor][runs][name]['mean'][1])
            p_offs_err.append(fit_log[flavor][runs][name]['offset'][1])

        order = np.argsort(x_axis)
        p_slope_s = np.array(p_slope)[order]
        p_mean_s = np.array(p_mean)[order]
        p_offs_s = np.array(p_offs)[order]
        x_axis_s = np.array(x_axis)[order]
        p_slope_err_s = np.array(p_slope_err)[order]
        p_mean_err_s = np.array(p_mean_err)[order]
        p_offs_err_s = np.array(p_offs_err)[order]

        for i in range(len(x_axis_s)):
            if flavor2 == 'TID':
                x_axis_c.append(self.dose[int(x_axis_s[i])])
                x_err.append(self.dose[int(x_axis_s[i])]*0.2)
            if flavor2 == 'Temperatur':
                x_axis_c.append(self.temp[int(x_axis_s[i])])
                x_err.append(2)

        if rel:
            p_mean_s = p_mean_s / p_mean_s[0]
            p_offs_s = p_offs_s / p_offs_s[0]
            p_mean_err_s = p_mean_err_s / p_mean_s[0]
            p_offs_err_s = p_offs_err_s / p_offs_s[0]

        label1 = str('slope')
        label2 = str('mean')
        label3 = str('offset')
        color1 = 'red'
        color2 = 'green'
        color3 = 'blue'
        ax1.errorbar(x_axis_c, p_slope_s, p_slope_err_s, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color1, capsize= 2, markeredgewidth=1, label=label1)
        if flavor2 == 'TID':
            ax1.semilogx()
        self.legend_dict[label1] = color1
        ax2.errorbar(x_axis_c, p_mean_s, p_mean_err_s, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color2, capsize= 2, markeredgewidth=1, label=label2)
        self.legend_dict[label2] = color2
        ax2.errorbar(x_axis_c, p_offs_s, p_offs_err_s, x_err, marker='.', fmt='o', linewidth=0.1, markersize='1', color=color3, capsize= 2, markeredgewidth=1, label=label3)
        if flavor2 == 'TID':
            ax2.semilogx()
        self.legend_dict[label3] = color3


        new_min = (min(p_slope_s) - 0.01)
        if new_min < scale1[0]:
            scale1[0] = new_min

        new_max = (max(p_slope_s) + 0.01)
        if new_max > scale1[1]:
            scale1[1] = new_max

        new_min = (min(p_offs_s) - min(p_offs) * 0.1)
        if new_min < scale2[0]:
            scale2[0] = new_min

        new_max = (max(p_offs_s) + max(p_offs) * 0.1)
        if new_max > scale2[1]:
            scale2[1] = new_max

        new_min = (min(p_mean_s) - min(p_mean) * 0.1)
        if new_min < scale2[0]:
            scale2[0] = new_min

        new_max = (max(p_mean_s) + max(p_mean) * 0.1)
        if new_max > scale2[1]:
            scale2[1] = new_max

        new_min = (float(min(x_axis_c)) - np.sqrt((float(min(x_axis_c)) * 0.1)**2))
        if new_min < scale2[0]:
            scale_x[0] = new_min

        new_max = (float(max(x_axis_c)) + float(max(x_axis_c)) * 0.1)
        if new_max > scale2[1]:
            scale_x[1] = new_max


    def fit_to_data(self, x, y, save_key, name, fit_length, cm=False):
        if flavor == 'LoadReg' or cm:
            fit_res, fit_res_err = self.poly_lsq(x[fit_length[0]:fit_length[1]], y[fit_length[0]:fit_length[1]], 1)
            fit_mean = np.mean(y[fit_length[0]:fit_length[1]])
            fit_mean_err = np.std(y[fit_length[0]:fit_length[1]])
        else:
            fit_res, fit_res_err = self.poly_lsq(x[fit_length[0]:], y[fit_length[0]:], 1)
            fit_mean = np.mean(y[fit_length[0]:])
            fit_mean_err = np.std(y[fit_length[0]:])

        if cm and name == 'CM_V':
            fit_res[0] *= float(save_key)
            fit_res_err[0] *= float(save_key)

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

        if not cm:
            self.fit_log[flavor]["run" + save_key][name]["mean"] = [float(fit_mean), float(fit_mean_err)]
        self.fit_log[flavor]["run" + save_key][name]["offset"] = [float(fit_res[1]), float(fit_res_err[1])]
        self.fit_log[flavor]["run" + save_key][name]["slope"] = [float(fit_res[0]), float(fit_res_err[0])]


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

    def poly_lsq(self, x, y, n, verbose=False):
        ''' Performs a polynomial least squares fit to the data,
        with errors! Uses scipy odrpack, but for least squares.

        IN:
           x,y (arrays) - data to fit
           n (int)      - polinomial order
           verbose      - can be 0,1,2 for different levels of output
                          (False or True are the same as 0 or 1)
           itmax (int)  - optional maximum number of iterations

        OUT:
           coeff -  polynomial coefficients, lowest order first
           err   - standard error (1-sigma) on the coefficients
        --Tiago, 20071114
        '''

        # http://www.scipy.org/doc/api_docs/SciPy.odr.odrpack.html
        # see models.py and use ready made models!!!!

        func = models.polynomial(n)
        mydata = odr.Data(x, y)
        myodr = odr.ODR(mydata, func)

        # Set type of fit to least-squares:
        myodr.set_job(fit_type=2)
        if verbose == 2: myodr.set_iprint(final=2)

        fit = myodr.run()

        # Display results:
        if verbose: fit.pprint()

        if fit.stopreason[0] == 'Iteration limit reached':
            print
            '(WWW) poly_lsq: Iteration limit reached, result not reliable!'

        # Results and errors
        coeff = fit.beta[::-1]
        err = fit.sd_beta[::-1]

        return coeff, err

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
                self.temp = [30.0, 15.0, 0.0, -15.0, -30.0, -40.0]
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
                              'NTC': {'loc': 7, 'title': 'NTC Temperature'}}

        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                if 'csv' in name and specifics in name and flavor in name:
                    filelist.append(name)
        # self.averaging(filelist)
        filelist = self.sort_filelist(filelist)

        for i, files in enumerate(filelist):
            collected_data[files] = self.file_to_array(files)
            # self.scan_parameter.append(i)
        if flavor2 == 'IV_NTC1':
            self.plot_ntc(data=collected_data, chip=chip_id, specifics=specifics)
            self.dump_plotdata()

            self.plot_iv_poly(filelist, name='V_in', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_out', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_offs', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='I_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_outpre', data=collected_data, chip=chip_id, flavor=flavor)
        elif flavor == 'IV2':
            self.plot_iv2(data=collected_data, chip=chip_id, flavor=flavor, specifics=specifics)
        elif flavor == 'CM':
            self.analysis_currentmirror(data=collected_data, chip=chip_id, specifics=specifics)
            self.plot_currentmirror(data=collected_data, chip=chip_id, specifics=specifics)
            self.dump_plotdata()
        elif 'LoadReg' in flavor:
            self.plot_ntc(data=collected_data, chip=chip_id, specifics=specifics, fit_length=[0, 15])
            self.dump_plotdata()

            self.create_plot('V_out', chip_id)

            self.create_plot('V_outpre', chip_id)

            self.create_plot('V_ref', chip_id)

            self.create_plot('I_ref', chip_id)

            self.create_plot('V_offs', chip_id)


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

            self.plot_iv_poly(filelist, name='V_out', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_offs', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='I_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_outpre', data=collected_data, chip=chip_id, flavor=flavor)

        else:
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
            self.plot_iv_poly(filelist, name='V_in', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_out', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_offs', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='I_ref', data=collected_data, chip=chip_id, flavor=flavor)
            self.plot_iv_poly(filelist, name='V_outpre', data=collected_data, chip=chip_id, flavor=flavor)

if __name__ == "__main__":
    root_path = os.getcwd()
    chips = Chip_overview()
    chip_id = 'RD53B_SLDO_BN007'
    flavor2 = 'IV_NTC1'
    flavor = 'LineReg'
    specifics = ''
    chips.create_iv_overview(chip_id, flavor, specifics, main=True)
#        chips.create_current_mirror_overview(reg_flavor = flavor)