import pyvisa as visa
from enum import Enum


class Function(Enum):
    DC_VOLTAGE = 'VOLT:DC'
    AC_VOLTAGE = 'VOLT:AC'
    DC_CURRENT = 'CURR:DC'
    AC_CURRENT = 'CURR:AC'
    RESISTANCE = 'RES'
    FOUR_WIRE_RESISTANCE = 'FRES'
    DIODE = 'DIO'
    CAPACITANCE = 'CAP'
    TEMPERATURE = 'TEMP'
    CONTINUITY = 'CON'
    FREQUENCY = 'FREQ'
    PERIOD = 'PER'
    VOLTAGE_RATIO = 'VOLT:RAT'


class DMM6500:

    def __init__(self, resource: visa.Resource):
        self.r = resource
        self.last_selected_function = None

    def reset(self):
        self.r.write('*RST')

    def set_function(self, func: Function):
        self.r.write(f':SENS:FUNC "{_scpi_func_name(func)}"')
        self.last_selected_function = func

    def set_range(self, max_expected_value: float):
        self.r.write(self._sense_prefix() + f'RANG {max_expected_value}')

    def set_auto_range(self, yes=True):
        self.r.write(self._sense_prefix() + f'RANG:AUTO {1 if yes else 0}')

    def set_auto_zero(self, yes=True):
        self.r.write(self._sense_prefix() + f'AZER {1 if yes else 0}')

    def set_nplc(self, nplc: float):
        self.r.write(self._sense_prefix() + f'NPLC {nplc}')

    def measure(self):
        return float(self.r.query(':MEAS?'))

    def _sense_prefix(self):
        if self.last_selected_function is None:
            raise Exception("No function selected yet")
        return f':SENS:{_scpi_func_name(self.last_selected_function)}:'


def _scpi_func_name(func: Function):
    return func.value
