'''
Testplot mit fit von der uni heidelberg
Nichtlineare Anpassung
Jens Wagner 07/2015
https://www.physi.uni-heidelberg.de/Einrichtungen/AP/python/fitting.html
actualized 03/2020 by Charlotte Perry
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def fit_wished_V(
        filename='data/IV0.csv',
        V=1,      # V = wished Voltage column number
        slope_min=0.8,
        slope_max=1.3,
        delta_min=-0.4,       # finetuning of slope-change-condition
        delta_max=0.4,
        data_label=r'$V_{in}$',
        x_axis=r'current $I$ / [A]',
        y_axis='voltage / [V]',
        plotname='IV Diagram\nfor ShuntLDO'
        ):

    '''
    Function to fit straight lines to given data,

    Output:
        fitvalues in shell,
        pdf with plot and fit values

    Variables:
        filename:        string with rel. path and name of the csv
        V = 1:           V = wished Voltage column number of csv
        slope_min:       minimal resistivity in kOhm
        slope_max:       maximal resistivity in kOhm
        delta_min:       finetuning of slope-change-condition: minimum change
        delta_max:       finetuning of slope-change-condition: maximum change
        data_label:      name of the measured y-axis quantity
        x_axis:          x-axis label
        y_axis:          y-axis label
        plotname:        Title of the plot

    '''

    # Data import (2 times is faster than 7 times per variable)
    data = np.loadtxt(filename, delimiter=',', unpack=True, skiprows=1)

    # plot the data without fitting here
    plt.figure(figsize=(8, 6))                # groesse des plots definieren
    plt.plot(
            data[0], data[V],
            marker='.', linestyle='',
            markersize=5, label=data_label)
    plt.xlabel(x_axis)                        # x label
    # plt.xlim([0, 1.2])                      # x axis limits
    plt.ylabel(y_axis)                        # y label
    plt.title(plotname)
    plt.grid(True)

    # ===========================================================================
    #     # plot for finding cuts
    # plt.plot(I_in[0:len(I_in)-3], slope, label='slope')
    # plt.plot(I_in[1:len(I_in)-3], deltas, label='difference to next slope')
    # plt.legend(loc='best')
    # plt.show()
    # ===============================================================================

    # Fit and conditions
    # Fitfunction = m*x + b
    def fitFunc(x, m, b):
        return m*x + b

    # initialize needed lists
    slope = []
    deltas = []
    xdata = []
    ydata = []
    index = []      # list of used indizes

    for i in range(0, len(data[0])-3):
        xvalues = [data[0][i], data[0][i+1], data[0][i+2], data[0][i+3]]
        yvalues = [data[V][i], data[V][i+1], data[V][i+2], data[V][i+3]]
        mopt = curve_fit(fitFunc, xvalues, yvalues, p0=[1, 1])[0]
        slope.append(mopt[0])
        if i > 0:
            delta = slope[i]-slope[i-1]
            deltas.append(delta)
            if ((slope_min < mopt[0] < slope_max)
                    and (delta_min < delta < delta_max)):
                xdata.append(data[0][i])
                ydata.append(data[V][i])
                index.append(i)

    # Fitparameter setting
    init_vals = [1, 1]                        # Fitparameter initialise (m, b)
    popt, pcov = curve_fit(fitFunc, xdata, ydata, p0=init_vals)
    # Fitparameter and covariancematrix
    perr = np.sqrt(np.diag(pcov))             # Standarderror

    print("m=", popt[0], ", Standarderror=", perr[0])
    print("b=", popt[1], ", Standarderror=", perr[1])

    # Diagramm mit angepasster Kurve zeichnen
    plt.plot(
            xdata, ydata,
            'g*', linestyle='', markersize=6,
            label=r'fitted data')
    plt.plot(data[0], fitFunc(data[0], *popt), label=r'fit-function')
    plt.legend(loc='best')  # further possible option: ,prop={'size':16}
    txtstr = '\n'.join((
        r"$m=%.3f\, \pm \, %.3f $ Standarderror" % (popt[0], perr[0], ),
        r"$b=%.3f\, \pm \, %.3f $ Standarderror" % (popt[1], perr[1], )))
    plt.text(1.1, 0.5, txtstr, va="bottom", ha="right")

    plt.savefig('IV-fit-easy.pdf')
    plt.show()                                # plot auch wirklich zeichnen


fit_wished_V(V=2, slope_min=-.1, slope_max=.3)
