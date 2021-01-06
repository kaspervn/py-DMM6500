# py-dmm6500

Helper functions to communicate with a Keithley DMM6500 multimeter via pyvisa

Note: Be sure to set the multimeter in SCPI communication mode

Example usage:
````
import pyvisa as visa
from DMM6500 import DMM6500

rm = visa.ResourceManager()
mm = DMM6500(rm.open_resource('USB::0x05e6::0x6500::*******::INSTR'))
mm.reset()
mm.set_function(Function.DC_VOLTAGE)
mm.set_auto_range()
mm.set_nplc(2)

print(mm.measure())
````