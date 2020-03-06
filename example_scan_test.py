#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# Test version by Charlotte Perry
# ------------------------------------------------------------
#
import logging
import numpy as np
from basil.dut import Dut
import time

# Talk to a Keithley and TTi devices via serial port using pySerial
dut = Dut('devices.yaml')
dut.init()

# Set devices quiet and test on name
devices = ['Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3']
for dev in devices:
    dut[dev].set_beeper(0)
    print(dut[dev].get_name())


# Scan Function definition
def IVin_scan(file_name='demo', max_Iin=1.2, rep=10, step_size=0.2,
              run_number=0):
    logging.info("Starting ...")

    # Set devices to Voltage measurement (Current=0, voltage limit=2)
    for dev in devices:
        for ch in [1, 2]:
            dut[dev].source_current(channel=ch)
            dut[dev].set_current(0, channel=ch)
            dut[dev].set_current_limit(1e-6, channel=ch)
            dut[dev].set_voltage_limit(2, channel=ch)

    # Activate all connected channels
    dut['Sourcemeter1'].on(channel=1)   # VDD
    dut['Sourcemeter1'].on(channel=2)   # Vref
    dut['Sourcemeter2'].on(channel=2)   # Vofs
    dut['Sourcemeter3'].on(channel=2)   # Iref

    #
    # hier moechte noch der TTI auf 2V begrenzt werden
    #

    irange = np.arange(0.0, max_Iin, step_size)
    print(irange)
    data = []

    logging.info("Start measuring ...")

    for iin in irange:
        dut['VDD1'].set_current_limit(iin)
        time.sleep(0.5)
        logging.info("Setting Current to %f" % iin)
        dut['VDD1'].set_enable(on=True)
        time.sleep(0.5)

#        vin = 0.0
        vdd = 0.0
        vref = 0.0
        vofs = 0.0
        iref = 0.0

        for _ in range(0, rep):
#            vin = vin + float(dut['VDD1'].get_voltage())
            vdd = vdd + float(dut['Sourcemeter1'].get_voltage(channel=1))
            vref = vref + float(dut['Sourcemeter1'].get_voltage(channel=2))
            vofs = vofs + float(dut['Sourcemeter2'].get_voltage(channel=2))
            iref = iref + float(dut['Sourcemeter3'].get_voltage(channel=2))/150000
            # print vin

        data.append([vdd/rep, vref/rep, vofs/rep, iref/rep])  #iin, vin/rep, 
#        iin = iin + step_size
        print(iin)

    logging.info("finished measuring ...")
    filename = file_name + "_" + str(run_number) + ".csv"
    np.savetxt(filename, data, delimiter=',',
               header='VDD, V_ref, V_ofs, I_ref')   # I_in, V_in, 
    print("writing to file %s" % filename)
    logging.info("Finish")


IVin_scan()
