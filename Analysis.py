'''
Created on 09.05.2018

@author: Florian
'''
import os
import csv
import logging
from os.path import isfile, join, normpath, normcase
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import threading
from IPython.core.pylabtools import figsize

root_path = os.getcwd()
threads = []
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")

def pathfinder(folder=None, chip_id=None, flavor=None, doubles = False): #navigate to output folder, if existing
    if not doubles:
        if normcase(folder) in os.listdir(root_path):
            os.chdir(normcase(root_path + "/" + folder))
            if flavor:
                try:
                    os.chdir(normcase(os.getcwd() + "/" + chip_id + "/" + flavor))
                except:
                    print(normcase(os.getcwd() + "/" + chip_id))
                    logging.error("No such path")
                    raise ValueError
            elif not flavor:
                try:
                    os.chdir(normcase(os.getcwd() + "/" + chip_id))
                except:
                    logging.error("No such path: %s" % normcase(os.getcwd() + "/" + chip_id))
                    logging.error("Current path: %s" % os.getcwd())
                    raise ValueError            
            working_dir = os.getcwd()
        else:
            logging.error("Output path %s not found" % folder)
            raise Exception
    elif doubles:
        if normcase(folder) in os.listdir(root_path):
            os.chdir(normcase(root_path + "/" + folder + "/" + "doubles"))
            if not flavor:
                try:
                    os.chdir(normcase(os.getcwd() + "/" + chip_id))
                except:
                    print(normcase(os.getcwd() + "/" + chip_id))
                    logging.error("No such path")
                    raise ValueError  
            else:
                raise ValueError          
            working_dir = os.getcwd()
    else:
        logging.error("Output path %s not found" % folder)
        raise Exception
    return working_dir
    
def file_grabber(folder=None, chip_id=None, flavor=None, file_type=None, average=False, doubles = False): #list of files in output folder, filtered by file type if desired
    filelist = []
    if flavor:
        for file in os.listdir(pathfinder(folder, chip_id, flavor, doubles=doubles)):
            if file_type:
                if file_type in file and "average" not in file:
                    filelist.append(file)
            else:
                filelist.append(file)
    elif not flavor:
        for file in os.listdir(pathfinder(folder, chip_id, doubles=doubles)):
            if file_type:
                if file_type in file and "average" not in file:
                    filelist.append(file)
            else:
                filelist.append(file)
#        print(filelist)
#        filelist = filelist  [3:7] 
    return filelist

def file_reading(file): #read csv file content and write into list. No check if file is actually csv or empty. TODO
    content = []
    with open(file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        try:
            header = next(spamreader)
            for i, row in enumerate(spamreader):
                content.append(row)
        except:
            print(file)
            raise ValueError
        file_content= np.empty(shape=(len(content), len(content[0])))
        for a in range(len(content)):
            for b in range(len(content[0])):
                file_content[a][b] = content[a][b]
                
    return {'header' : header, 'data': file_content}

def file_to_array(file):
    header = np.genfromtxt(file, dtype=None, delimiter = ',', max_rows = 1)
    data = np.genfromtxt(file, float, delimiter=',', skip_header=1)
    rows = len(data)
    cols = len(data[0])
    return {'header': header, 'data': data, 'rows' : rows, 'cols' : cols}

def analysis(folder=None, files=None, chip_id=None, flavor=None, file_type = 'csv', average = True, doubles=False):
    start = time.clock()
    logging.info("Starting...")
    if not files:
        filelist = file_grabber(folder = folder, chip_id = chip_id, flavor=flavor, file_type=file_type, doubles=doubles)
    elif files:
        filelist = files
    raw_data, rows, cols = [], [], []
    files = len(filelist)
    for file in filelist:
        filecontent = file_to_array(file)
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

    try:
        with open(chip_id + '_' + flavor + '_' + 'average.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            spamwriter.writerow(header)
            for row in interpreted_data[0]:
                spamwriter.writerow(row)
        with open(chip_id + '_' + flavor + '_' + 'average_dev.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            spamwriter.writerow(header)
            for row in interpreted_data[1]:
                spamwriter.writerow(row)

                
    finally:
        pass
#    os.chdir(root_path)
    return interpreted_data


def plot_iv(data = None, chip_id = '0x000', flavor = 'VDDD', reg_flavor = None, average = False, filename = "file", fit_length = 10):
    iin, vin, vout, vref, voffs, delta_iin, delta_vin, delta_vout, delta_vref, delta_voffs = [],[],[],[],[],[],[],[],[],[]
    
    fig, (ax1) = plt.subplots(1, sharex=True)
#    ax_text.axis('off')
    fig.subplots_adjust(top=0.85, bottom=0.15)
    y_coord = 0.7
    fig.text(.95, y_coord-0.1, 'RD53A preliminary' , fontsize=12, color='#07529a', transform=fig.transFigure)
    fig.text(.95, y_coord, 'Chip S/N: ' + chip_id, fontsize=12, color='#07529a', transform=fig.transFigure)


    if average:
        logging.info("Plotting averaged values")
        for row in data[0]:
            iin.append(row[0])
            if reg_flavor == 'VDDA':
                vin.append(row[5])
                vout.append(row[6])
                vref.append(row[7])
                voffs.append(row[8])
            elif reg_flavor == 'VDDD':
                vin.append(row[1])
                vout.append(row[2])
                vref.append(row[3])
                voffs.append(row[4])
            else:
                raise RuntimeError             
        for row in data[1]:
            delta_iin.append(row[0])
            if reg_flavor == 'VDDA':
                delta_vin.append(row[5])
                delta_vout.append(row[6])
                delta_vref.append(row[7])
                delta_voffs.append(row[8])
            elif reg_flavor == 'VDDD':
                delta_vin.append(row[1])
                delta_vout.append(row[2])
                delta_vref.append(row[3])
                delta_voffs.append(row[4])
            else:
                raise RuntimeError

#        fig.text(0.4, 0.5, 'RD53 Internal', fontsize=16, color='r', rotation=45, bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', alpha=0.7), transform=fig.transFigure)

        
        ax1.errorbar(iin, vin, yerr = delta_vin, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='red', label='Input Voltage')
        ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red')
        ax1.errorbar(iin, vout, yerr = delta_vout, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='blue', label='Output Voltage')
        ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue')
        ax1.errorbar(iin, vref, yerr = delta_vref, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='green', label='Reference Voltage')
        ax1.plot(iin, vref, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='green')
        ax1.errorbar(iin, voffs, yerr = delta_voffs, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='olive', label='Offset Voltage')
        ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='olive')
        
        x = np.polyfit(iin[-fit_length:], vin[-fit_length:], 1)
        y = np.polyfit(iin[-fit_length:], voffs[-fit_length:], 1)
        u_in = []
        offs = []
        offset_mean = np.mean(voffs[-fit_length:]) * 2
        for i in range(len(iin)):
            u_in.append(iin[i] * x[0] + x[1])
            offs.append(iin[i] * y[0] + y[1])
        print(y[0], y[1])
            
        ax1.plot(iin, u_in, linestyle='-', linewidth= 0.05, markersize = '.8', color='red', label = 'Reff from input Voltage fit = %.2f Ohm, offset = %.2f V' % (x[0], x[1]))
        ax1.plot(iin, offs, linestyle='-', linewidth= 0.05, markersize = '.8', color='olive', label = 'Offset from measurement = %.2f V, Slope = %.2f V/A' % (offset_mean,y[0]))
        
    else:
        logging.info("Plotting from file %s" % filename)
        for row in data:
            iin.append(row[0])
            if reg_flavor == 'VDDA':
                vin.append(row[5])
                vout.append(row[6])
                vref.append(row[7])
                voffs.append(row[8])
            elif reg_flavor == 'VDDD':
                vin.append(row[1])
                vout.append(row[2])
                vref.append(row[3])
                voffs.append(row[4]) 
            
        ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red', label='Input Voltage')
        ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue', label='Output Voltage')
        ax1.plot(iin, vref, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='green', label='Reference Voltage')
        ax1.plot(iin, voffs, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='olive', label='Offset Voltage')
    
    if not average:
        ax1.set_title('SLDO Input IV')
    elif average:
        ax1.set_title('SLDO Averaged Input IV')
    ax1.legend()
    lgd = ax1.legend(bbox_to_anchor=(1.05, 0.24), loc=2, borderaxespad=0.)
    ax1.grid()
    ax1.set_ylabel('Voltage [V]')
    ax1.set_xlabel('Input Current [A]')
    ax1.axis([0,1.2,0,2.1])
#    plt.tight_layout()
    if average:
        os.chdir(pathfinder(folder=folder, chip_id=chip_id, flavor=flavor))
        logging.info("Saving average plot")
        try:
            fig.savefig(chip_id + '_' + flavor + '_averaged_' + reg_flavor + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig(chip_id + '_' + flavor + '_averaged_' + reg_flavor + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Average plot could not be saved" )
            raise ValueError
        logging.info("Finished.")
    
    else:
        logging.info("Saving plot %s" % filename)
        try:
            fig.savefig(filename + '_' + reg_flavor + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig(filename + '_' + reg_flavor + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
    logging.info("Finished.")
    plt.close()

def plot_current_mirror(data = None, chip_id = '0x000', flavor = 'VDDD', reg_flavor = 'VDDA', average = False, joint = False, filename = "file"):
    iin, vin, vout, vext, mirror, delta_iin, delta_vin, delta_vout, delta_vext, delta_mirror = [],[],[],[],[],[],[],[],[],[]
    
    fig, (ax1) = plt.subplots(1, sharex=True)
#    ax_text.axis('off')
    fig.subplots_adjust(top=0.85, bottom=0.15)
    y_coord = 0.8
    fig.text(1, y_coord-0.1, 'RD53A preliminary' , fontsize=12, color='#07529a', transform=fig.transFigure)
    fig.text(1, y_coord, 'Chip S/N: ' + chip_id, fontsize=12, color='#07529a', transform=fig.transFigure)
    ax2 = ax1.twinx()


    if average:
        logging.info("Plotting averaged values")
        for row in data[0]:
            iin.append(row[0])
            if reg_flavor == 'VDDA':
                vin.append(row[1])
                vout.append(row[2])
                vext.append(row[3])
                mirror.append(row[4])
            elif reg_flavor == 'VDDD':
                vin.append(row[5])
                vout.append(row[6])
                vext.append(row[7])
                mirror.append(row[8])
        for row in data[1]:
            delta_iin.append(row[0])
            if reg_flavor == 'VDDA':
                delta_vin.append(row[1])
                delta_vout.append(row[2])
                delta_vext.append(row[3])
                delta_mirror.append(row[4])
            elif reg_flavor == 'VDDD':
                delta_vin.append(row[5])
                delta_vout.append(row[6])
                delta_vext.append(row[7])
                delta_mirror.append(row[8])

#        fig.text(0.4, 0.5, 'RD53 Internal', fontsize=16, color='r', rotation=45, bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', alpha=0.7), transform=fig.transFigure)

        ax1.errorbar(iin, vin, yerr = delta_vin, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='red', label='Input Voltage')
#        ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red')
        ax1.errorbar(iin, vout, yerr = delta_vout, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='blue', label='Output Voltage')
#        ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue')
        ax1.errorbar(iin, vext, yerr = delta_vext, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='green', label='Vext')
#        ax1.plot(iin, vext, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='green')
        ax2.errorbar(iin, mirror, yerr = delta_mirror, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='olive', label='Current Mirror Ratio')
#        ax2.plot(iin, mirror, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='olive')
        
        z = np.polyfit(iin[-40:], vext[-40:], 1)

        u_in = []
        u_ext = []
        u_theo = []
        u_expect = []
        for i in range(len(iin)):
            u_ext.append(z[0] * iin[i] + z[1])
            if vin[i] <= 1:
                u_theo.append(0)
            elif vin[i] > 1:
                u_theo.append(vin[i]-1)

        x = np.polyfit(iin[-40:], vin[-40:], 1)
        y = np.polyfit(iin[-40:], u_theo[-40:], 1)

        for i in range(len(iin)):
            u_expect.append(y[0]*iin[i]+y[1])
            u_in.append(iin[i] * x[0] + x[1])

        print("Fitted Rext expectation", y)
        print("Fitted Rext measurement", z)
        
        ''' For ideal case '''
        
        v_ext_theo = []
        
        for i in range(len(iin)):
            v_ext_theo.append((iin[i] * 806)/1000)
        
        ax1.plot(iin, u_ext, linestyle='-', linewidth= 0.05, markersize = '.8', color='green', label = 'Reff from fit = %.2f Ohm' %z[0])
        ax1.plot(iin, u_in, linestyle='-', linewidth= 0.05, markersize = '.8', color='red', label = 'Reff from input Voltage fit = %.2f Ohm' % x[0])
        ax1.plot(iin, u_expect, linestyle='-', linewidth= 0.05, markersize = '.8', color='black', label = 'Reff from expectation = %.2f Ohm' %y[0])
        ax1.plot(iin, v_ext_theo, linestyle='-', linewidth= 0.05, markersize = '.8', color='purple', label = 'Vext according to Vext = (Iin Rext) / k')
        
    else:
        logging.info("Plotting from file %s" % filename)
        for row in data:
            iin.append(row[0])
            if reg_flavor == 'VDDA':
                vin.append(row[1])
                vout.append(row[2])
                vext.append(row[3])
                mirror.append(row[4])
            if reg_flavor == 'VDDD':
                vin.append(row[5])
                vout.append(row[6])
                vext.append(row[7])
                mirror.append(row[8])
            
        ax1.plot(iin, vin, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red', label='Input Voltage')
        ax1.plot(iin, vout, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue', label='Output Voltage')
        ax1.plot(iin, vext, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='green', label='Vext')
        ax2.plot(iin, mirror, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='olive', label='Current Mirror Ratio')
    
    
    ax1.set_title('SLDO' +' Current Mirror ' + reg_flavor)
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    lgd = ax2.legend(lines + lines2, labels + labels2, bbox_to_anchor=(1.2, .25), loc=2, borderaxespad=0.)
#    lgd = ax2.legend(lines+lines2, labels+labels2, bbox_to_anchor=(0.42,1))
    ax1.grid()
    ax1.set_ylabel('Voltage [V]')
    ax1.set_xlabel('Input Current [A]')
    ax2.set_ylabel('Current Mirror Ratio')
    ax1.axis([0,max(iin)+max(iin)/10,0,2.1])
    ax2.axis([0,max(iin)+max(iin)/10,0,2000])
#    plt.tight_layout()
    if average:
        os.chdir(pathfinder(folder=folder, chip_id=chip_id, flavor=flavor))
        logging.info("Saving average plot")
        try:
            fig.savefig('averaged_' + reg_flavor + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig('averaged_' + reg_flavor + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Average plot could not be saved" )
            raise ValueError
        logging.info("Finished.")
    
    else:
        logging.info("Saving plot %s" % filename)
        try:
            fig.savefig(filename + '_' + reg_flavor + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig(filename + "_" + reg_flavor + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError

    logging.info("Finished.")
    plt.close()
    
    
    
def plot_current_balancing(data = None, chip_id = '0x000', flavor = 'VDDD', average = False, filename = "file", doubles = False, quads = False):        
    iin, iin_vdda, vin_vdda, vout_vdda, iin_vddd, vin_vddd, vout_vddd, delta_iin, delta_iin_vdda, delta_vin_vdda, delta_vout_vdda, delta_iin_vddd, delta_vin_vddd, delta_vout_vddd = [],[],[],[],[],[],[],[],[],[],[],[],[],[]
    
    logging.info("Plotting from file %s" % filename)
    
    if not doubles:
        fig, (ax1, ax2) = plt.subplots(2, sharex=True, gridspec_kw = {'height_ratios':[1.5, 1]}, figsize=(6,6))
    elif doubles:
        fig, (ax1) = plt.subplots(1, sharex=True)
    fig.subplots_adjust(top=0.85, bottom=0.15)
    y_coord = 0.8
    fig.text(1., y_coord, 'Chip S/N: ' + chip_id, fontsize=12, color='#07529a', transform=fig.transFigure)


    if average:
        
        if doubles and not quads:
            chip_a_iin_vdda, chip_a_iin_vddd, chip_b_iin_vdda, chip_b_iin_vddd, delta_chip_a_iin_vdda, delta_chip_a_iin_vddd, delta_chip_b_iin_vdda, delta_chip_b_iin_vddd = [],[],[],[],[],[],[],[]
            for row in data[0]:
                chip_a_iin_vdda.append(row[0])
                chip_a_iin_vddd.append(row[1])
                chip_b_iin_vdda.append(row[2])
                chip_b_iin_vddd.append(row[3])
                iin.append(row[4])
            for row in data[1]:
                delta_chip_a_iin_vdda.append(row[0])
                delta_chip_a_iin_vddd.append(row[1])
                delta_chip_b_iin_vdda.append(row[2])
                delta_chip_b_iin_vddd.append(row[3])
                delta_iin.append(row[4])
                
            ax1.errorbar(iin, chip_a_iin_vdda, yerr = delta_chip_a_iin_vdda, xerr = delta_iin, linestyle='', marker='', linewidth= .1, markersize = '1', color='red', label='Chip A Analog Input Current')
            ax1.plot(iin, chip_a_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='red')
            ax1.errorbar(iin, chip_a_iin_vddd, yerr = delta_chip_a_iin_vddd, xerr = delta_iin, linestyle='', marker='', linewidth= .1, markersize = '1', color='blue', label='Chip A Digital Input Current')
            ax1.plot(iin, chip_a_iin_vddd, linestyle='-', linewidth= 0.2, markersize = '.5', color='blue')
            ax1.errorbar(iin, chip_b_iin_vdda, yerr = delta_chip_b_iin_vdda, xerr = delta_iin, linestyle='', marker='', linewidth= .1, markersize = '1', color='green', label='Chip B Analog Input Current')
            ax1.plot(iin, chip_b_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='green')
            ax1.errorbar(iin, chip_b_iin_vddd, yerr = delta_chip_b_iin_vddd, xerr = delta_iin, linestyle='', marker='', linewidth= .1, markersize = '1', color='yellow', label='Chip B Digital Input Current')
            ax1.plot(iin, chip_b_iin_vddd, linestyle='-', linewidth= 0.2, markersize = '.5', color='yellow')

        elif doubles and quads:
            chip_a_iin_vdda, chip_a_iin_vddd, chip_b_iin_vdda, chip_b_iin_vddd, chip_c_iin_vdda, chip_c_iin_vddd, chip_d_iin_vdda, chip_d_iin_vddd, iin_vddd, iin_vdda = [],[],[],[],[],[],[],[],[],[]
            delta_chip_a_iin_vdda, delta_chip_a_iin_vddd, delta_chip_b_iin_vdda, delta_chip_b_iin_vddd, delta_chip_c_iin_vdda, delta_chip_c_iin_vddd, delta_chip_d_iin_vdda, delta_chip_d_iin_vddd, delta_iin_vddd, delta_iin_vdda = [],[],[],[],[],[],[],[],[],[]
            for row in data[0][0]:
                chip_a_iin_vddd.append(row[0])
                chip_b_iin_vddd.append(row[1])
                chip_c_iin_vddd.append(row[2])
                chip_d_iin_vddd.append(row[3])
                iin_vddd.append(row[4])
            for row in data[1][0]:
                chip_a_iin_vdda.append(row[0])
                chip_b_iin_vdda.append(row[1])
                chip_c_iin_vdda.append(row[2])
                chip_d_iin_vdda.append(row[3])
                iin_vdda.append(row[4])
            for row in data[0][1]:
                delta_chip_a_iin_vddd.append(row[0])
                delta_chip_b_iin_vddd.append(row[1])
                delta_chip_c_iin_vddd.append(row[2])
                delta_chip_d_iin_vddd.append(row[3])
                delta_iin_vddd.append(row[4])
            for row in data[1][1]:
                delta_chip_a_iin_vdda.append(row[0])
                delta_chip_b_iin_vdda.append(row[1])
                delta_chip_c_iin_vdda.append(row[2])
                delta_chip_d_iin_vdda.append(row[3])
                delta_iin_vdda.append(row[4])
                

            ax1.errorbar(iin_vdda, chip_a_iin_vdda, yerr = delta_chip_a_iin_vdda, xerr = delta_iin_vdda, linestyle='', marker='', linewidth= .1, markersize = '1', color='firebrick', label='Chip A Analog Input Current')
            ax1.plot(iin_vdda, chip_a_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='firebrick')
            ax1.errorbar(iin_vddd, chip_a_iin_vddd, yerr = delta_chip_a_iin_vddd, xerr = delta_iin_vddd, linestyle='', marker='', linewidth= .1, markersize = '1', color='red', label='Chip A Digital Input Current')
            ax1.plot(iin_vddd, chip_a_iin_vddd, linestyle=':', linewidth= 0.2, markersize = '.5', color='red')
            ax1.errorbar(iin_vdda, chip_b_iin_vdda, yerr = delta_chip_b_iin_vdda, xerr = delta_iin_vdda, linestyle='', marker='', linewidth= .1, markersize = '1', color='navy', label='Chip B Analog Input Current')
            ax1.plot(iin_vdda, chip_b_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='navy')
            ax1.errorbar(iin_vddd, chip_b_iin_vddd, yerr = delta_chip_b_iin_vddd, xerr = delta_iin_vddd, linestyle='', marker='', linewidth= .1, markersize = '1', color='blue', label='Chip B Digital Input Current')
            ax1.plot(iin_vddd, chip_b_iin_vddd, linestyle=':', linewidth= 0.2, markersize = '.5', color='blue')
            ax1.errorbar(iin_vdda, chip_c_iin_vdda, yerr = delta_chip_c_iin_vdda, xerr = delta_iin_vdda, linestyle='', marker='', linewidth= .1, markersize = '1', color='olive', label='Chip C Analog Input Current')
            ax1.plot(iin_vdda, chip_c_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='olive')
            ax1.errorbar(iin_vddd, chip_c_iin_vddd, yerr = delta_chip_c_iin_vddd, xerr = delta_iin_vddd, linestyle='', marker='', linewidth= .1, markersize = '1', color='green', label='Chip C Digital Input Current')
            ax1.plot(iin_vddd, chip_c_iin_vddd, linestyle=':', linewidth= 0.2, markersize = '.5', color='green')
            ax1.errorbar(iin_vdda, chip_d_iin_vdda, yerr = delta_chip_d_iin_vdda, xerr = delta_iin_vdda, linestyle='', marker='', linewidth= .1, markersize = '1', color='goldenrod', label='Chip D Analog Input Current')
            ax1.plot(iin_vdda, chip_d_iin_vdda, linestyle='-', linewidth= 0.2, markersize = '.5', color='goldenrod')
            ax1.errorbar(iin_vddd, chip_d_iin_vddd, yerr = delta_chip_d_iin_vddd, xerr = delta_iin_vddd, linestyle='', marker='', linewidth= .1, markersize = '1', color='yellow', label='Chip D Digital Input Current')
            ax1.plot(iin_vddd, chip_d_iin_vddd, linestyle=':', linewidth= 0.2, markersize = '.5', color='yellow')

        else:
            for row in data[0]:
                iin_vdda.append(row[0])
                vin_vdda.append(row[1])
                vout_vdda.append(row[2])
                iin_vddd.append(row[3])
                vin_vddd.append(row[4])
                vout_vddd.append(row[5])
                iin.append(row[6])
            for row in data[1]:
                delta_iin_vdda.append(row[0])
                delta_vin_vdda.append(row[1])
                delta_vout_vdda.append(row[2])
                delta_iin_vddd.append(row[3])
                delta_vin_vddd.append(row[4])
                delta_vout_vddd.append(row[5])
                delta_iin.append(row[6])
    
    #        fig.text(0.4, 0.5, 'RD53 Internal', fontsize=16, color='r', rotation=45, bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', alpha=0.7), transform=fig.transFigure)
    
            ax1.errorbar(iin, iin_vdda, yerr = delta_iin_vdda, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='red', label='Analog Input Current')
            ax1.plot(iin, iin_vdda, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red')
            ax1.errorbar(iin, iin_vddd, yerr = delta_iin_vddd, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='blue', label='Digital Input Current')
            ax1.plot(iin, iin_vddd, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue')
        
            ax2.errorbar(iin, vout_vdda, yerr = delta_iin_vdda, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='red', label='Analog Output Voltage')
            ax2.plot(iin, vout_vdda, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red')
            ax2.errorbar(iin, vout_vddd, yerr = delta_iin_vddd, xerr = delta_iin, linestyle='', marker='.', linewidth= 0.7, markersize = '2', color='blue', label='Digital Output Voltage')
            ax2.plot(iin, vout_vddd, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue')

        #expected from deviation in sense resistors
        if not quads:
            R_tot = 1/(1/1.03 + 1/1.033+1/1.029+1/1.031)
            u_i = []
            i_1, i_2, i_3, i_4 = [],[],[],[]
            for i in range(len(iin)):
                u_i.append(R_tot * iin[i])
                i_1.append(u_i[i]/1.03)
        elif quads:
            R_tot = 1/(1/1.03 + 1/1.033+1/1.029+1/1.031)
            u_i = []
            i_1, i_2, i_3, i_4 = [],[],[],[]
            for i in range(len(iin_vdda)):
                u_i.append(R_tot * iin_vdda[i])
                i_1.append(0.5*u_i[i]/1.03)        
        ax1.plot(iin_vdda, i_1, linestyle='-', linewidth= 0.05, markersize = '.5', color='black')
        
    else:
        if doubles:
            chip_a_iin_vdda, chip_a_iin_vddd, chip_b_iin_vdda, chip_b_iin_vddd = [],[],[],[]
            for row in data:
                chip_a_iin_vdda.append(row[0])
                chip_a_iin_vddd.append(row[1])
                chip_b_iin_vdda.append(row[2])
                chip_b_iin_vddd.append(row[3])
                iin.append(row[4])
            
            ax1.plot(iin, chip_a_iin_vdda, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red', label='Chip A Analog Input Current')
            ax1.plot(iin, chip_a_iin_vddd, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue', label='Chip A Digital Input Current')
            ax1.plot(iin, chip_b_iin_vdda, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='green', label='Chip B Analog Input Current')
            ax1.plot(iin, chip_b_iin_vddd, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='yellow', label='Chip B Digital Input Current')            
       
        else:
            for row in data:
                iin_vdda.append(row[0])
                vin_vdda.append(row[1])
                vout_vdda.append(row[2])
                iin_vddd.append(row[3])
                vin_vddd.append(row[4])
                vout_vddd.append(row[5])
                iin.append(row[6])
                
            ax1.plot(iin, iin_vdda, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='red', label='Analog Input Current')
            ax1.plot(iin, iin_vddd, linestyle='-', marker='.', linewidth= 0.1, markersize = '2', color='blue', label='Digital Input Current')
            
            ax2.plot(iin, vout_vdda, linestyle='-.', marker='.', linewidth= 0.05, markersize = 0.5, color='red', label='Analog Output Voltage')
            ax2.plot(iin, vout_vddd, linestyle='-.', marker='.', linewidth= 0.05, markersize = 0.5, color='blue', label='Digital Output Voltage')
    
    ax1.set_title('SLDO' +' Current Balancing')
    lgd = ax1.legend(bbox_to_anchor=(0, 1), loc=2, borderaxespad=0.)
    ax1.grid()
    ax1.set_ylabel('Current [A]')
    ax1.set_xlabel('Shared Input Current [A]')
    if not quads:
        ax1.axis([0,4,0,1.2])
    if quads:
        ax1.axis([0,5,0,0.8])
    if not doubles:
        ax1.axis([0,5,0,1.5])
        lgd = ax1.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax2.grid()
        ax2.set_title('SLDO' + ' Output IV')
        lgd = ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax2.set_ylabel('Voltage [V]')
        ax2.set_xlabel('Shared Input Current [A]')
        ax2.tick_params('y')
        ax2.axis([0,5,0,1.5])
    plt.tight_layout()
    if average:
        print(doubles)
        print(os.getcwd())
        os.chdir(pathfinder(folder=folder, chip_id=chip_id, flavor=None, doubles=doubles))
        logging.info("Saving average plot")
        try:
            fig.savefig('averaged' + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig('averaged' + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Average plot could not be saved" )
            raise ValueError
        logging.info("Finished.")
    
    else:
        logging.info("Saving plot %s" % filename)
        try:
            fig.savefig(filename + '.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
            fig.savefig(filename + '.png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        except:
            logging.error("Plot %s could not be saved" % filename)
            raise ValueError
    logging.info("Finished.")
    plt.close()


import re 

def sorted_nicely( l ): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


def current_balancing(folder, chip_id, flavor=None, file=None, doubles=False, quads = False):
    if not file:
        for file in file_grabber(folder, chip_id, flavor=None, file_type = 'csv', doubles=doubles):
            file_name = file.split(".csv")[0]
            plot_current_balancing(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, average=False, filename=file_name, doubles=doubles)
        if not quads:
            interpreted_data = analysis(folder=folder, chip_id=chip_id, flavor=flavor, file_type='csv', average=True, doubles=doubles)
            plot_current_balancing(data = interpreted_data, chip_id =  chip_id, flavor=None, average=True, filename=file_name, doubles=doubles)
    elif file:
        for file in file:
            file_name = file.split(".csv")
            plot_current_balancing(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, average=False, filename=file_name, doubles=doubles)
    if quads:
        files = file_grabber(folder, chip_id, flavor=None, file_type = 'csv', doubles=True)
        half = len(files)/2
        files = sorted_nicely(files)
        print(files)
        interpreted_data_vddd = analysis(folder=folder, files = files[:half], chip_id=chip_id, flavor=flavor, file_type='csv', average=True, doubles=doubles)
        interpreted_data_vdda = analysis(folder=folder, files = files[half:], chip_id=chip_id, flavor=flavor, file_type='csv', average=True, doubles=doubles)
        interpreted_data = [interpreted_data_vddd, interpreted_data_vdda]
        plot_current_balancing(data = interpreted_data, chip_id =  chip_id, flavor=None, average=True, filename=file_name, doubles=doubles, quads = True)

def input_iv(folder, chip_id, flavor=None, reg_flavor = None, file=None, fit_length = 10):
    if not file:
        for file in file_grabber(folder, chip_id, flavor=flavor, file_type = 'csv'):
            file_name = file.split(".csv")[0]
            plot_iv(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, reg_flavor = 'VDDA', average=False, fit_length = fit_length, filename=file_name)
            plot_iv(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, reg_flavor = 'VDDD', average=False, fit_length = fit_length, filename=file_name)
        interpreted_data = analysis(folder=folder, chip_id=chip_id, flavor=flavor, file_type='csv', average=True)
        plot_iv(data = interpreted_data, chip_id =  chip_id, flavor=flavor, reg_flavor = 'VDDA', average=True, fit_length = fit_length,  filename=None)            
        plot_iv(data = interpreted_data, chip_id =  chip_id, flavor=flavor, reg_flavor = 'VDDD', average=True, fit_length = fit_length,  filename=None)
    elif file:
        file_name = file.split(".csv")
        plot_iv(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=flavor,reg_flavor = 'VDDA', average=False, fit_length = fit_length,  filename=file_name)
        plot_iv(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=flavor,reg_flavor = 'VDDD', average=False, fit_length = fit_length,  filename=file_name)
        
def current_mirror(folder, chip_id, flavor=None, file=None):
    if not file:
        for file in file_grabber(folder, chip_id, flavor=flavor, file_type = 'csv'):
            file_name = file.split(".csv")[0]
            plot_current_mirror(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, average=False, reg_flavor = 'VDDA', filename=file_name)
            plot_current_mirror(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=None, average=False, reg_flavor = 'VDDD', filename=file_name)
        interpreted_data = analysis(folder=folder, chip_id=chip_id, flavor=flavor, file_type='csv', average=True)
        plot_current_mirror(data = interpreted_data, chip_id =  chip_id, flavor=flavor, average=True, reg_flavor= 'VDDA', filename=None)
        plot_current_mirror(data = interpreted_data, chip_id =  chip_id, flavor=flavor, average=True, reg_flavor = 'VDDD', filename=None)
    elif file:
        file_name = file.split(".csv")
        plot_current_mirror(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=flavor, average=False, reg_flavor = 'VDDA', filename=file_name)
        plot_current_mirror(data = file_to_array(file)['data'], chip_id =  chip_id, flavor=flavor, average=False, reg_flavor = 'VDDD', filename=file_name)


'''
------------------------------------------------------------------------------------------------------------------------------
'''

if __name__ == "__main__": 
    
    starttime = time.clock()
    folder = normcase('output')
    #chips = ["0x0746+0x074B"]
    chips = ["0x0B75"]
    
    for chip_id in chips:
        os.chdir(pathfinder(folder, chip_id, flavor=None, doubles = False))
        #current_balancing(folder=folder, chip_id=chip_id, doubles = True, quads = True)
        
        input_iv(folder=folder, chip_id=chip_id, flavor='25degC', fit_length = 30)
        #input_iv(folder=folder, chip_id=chip_id, flavor='+5degC', fit_length = 30)
        #input_iv(folder=folder, chip_id=chip_id, flavor='-10degC', fit_length = 20)
        #input_iv(folder=folder, chip_id=chip_id, flavor='-25degC', fit_length = 20)
        #input_iv(folder=folder, chip_id=chip_id, flavor='-40degC', fit_length = 15)
        #input_iv(folder=folder, chip_id=chip_id, flavor='IV', fit_length = 15)
        
        #current_mirror(folder=folder, chip_id=chip_id, flavor='Mirror')
        #current_mirror(folder=folder, chip_id="0x0746", flavor='Mirror_forced_BG')
        #current_mirror(folder=folder, chip_id="0x0746", flavor='Mirror_commonLV')
    
    stoptime = time.clock()
    print(stoptime-starttime)


