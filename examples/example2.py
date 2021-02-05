import pyvisa as visa

from DMM6500 import DMM6500, DummyVisaResource
from DMM6500_SCPI import Function, Screen

try:
    rm = visa.ResourceManager()
    mm = DMM6500(rm.open_resource('USB::0x05e6::0x6500::*******::INSTR'))
except ValueError:
    print('Could not connect to multimeter for example. Using virtual dummy multimeter')
    mm = DMM6500(DummyVisaResource())

mm.reset()
mm.apply_settings({
        'function': Function.DC_CURRENT,
        'range': 'auto',
        'nplc': 1.0,
        'screen': Screen.SWIPE_USER})

mm.display_user_text(1, "Hello")
mm.display_user_text(2, "Pizza")

print(mm.measure())
