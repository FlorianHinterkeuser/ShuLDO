import time
import logging
import csv
import os.path
import time
import numpy as np
import math
import yaml

from scan_misc import Misc
from basil.dut import Dut

def current_mirror():
    dut = Dut('v_rext_measure.yaml')
    dut.init()
    misc = Misc(dut=dut)

    dut = Dut('v_rext_measure.yaml')
    dut.init()
    misc = Misc(dut=dut)
    vrext = {}

    with open('vext_log.yaml', 'a') as outfile:
        key = str(time.time())
        vrext[key] = float(dut["Multimeter2"].get_voltage())
        yaml.dump(vrext, outfile)