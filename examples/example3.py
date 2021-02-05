import pyvisa as visa

from DMM6500 import DMM6500, DummyVisaResource
from DMM6500_SCPI import Function

try:
    rm = visa.ResourceManager()
    mm = DMM6500(rm.open_resource('USB::0x05e6::0x6500::*******::INSTR'))
except ValueError:
    print('Could not connect to multimeter for example. Using virtual dummy multimeter')
    mm = DMM6500(DummyVisaResource())

mm.reset()
mm.set_function(Function.DC_VOLTAGE)
mm.range = 100000  # certainly too big. Will create error message on screen

print('errors:')
print(mm.get_all_errors())
