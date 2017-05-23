from basil.dut import Dut

import time

if __name__ == "__main__":
    
    dut = Dut('sensirionEKH4.yaml')
    dut.init()
    
    while True:
        print "____"
        print dut['Thermohygrometer'].get_temperature()
        print dut['Thermohygrometer'].get_humidity()
        print dut['Thermohygrometer'].get_dew_point()
        time.sleep(10)