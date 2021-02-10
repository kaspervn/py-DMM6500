import inspect
import re
from enum import Enum
from typing import Callable


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

    def __str__(self):
        return self.value


class Screen(Enum):
    HOME = 'HOME'
    HOME_LARGE = 'HOME_LARGE_READING'
    READING_TABLE = 'READING_TABLE'
    GRAPH = 'GRAPH'
    HISTOGRAM = 'HISTOGRAM'
    SWIPE_FUNCTIONS = 'SWIPE_FUNCTIONS'
    SWIPE_GRAPH = 'SWIPE_GRAPH'
    SWIPE_SECONDARY = 'SWIPE_SECONDARY'
    SWIPE_SETTINGS = 'SWIPE_SETTINGS'
    SWIPE_STATISTICS = 'SWIPE_STATISTICS'
    SWIPE_USER = 'SWIPE_USER'
    SWIPE_CHANNEL = 'SWIPE_CHANNEL'
    SWIPE_NONSWITCH = 'SWIPE_NONSWITCH'
    SWIPE_SCAN = 'SWIPE_SCAN'
    CHANNEL_CONTROL = 'CHANNEL_CONTROL'
    CHANNEL_SETTINGS = 'CHANNEL_SETTINGS'
    CHANNEL_SCAN = 'CHANNEL_SCAN'
    PROCESSING = 'PROCESSING'

    def __str__(self):
        return self.value


query_templates = {
    # commands
    'reset':                    ['*RST'],
    'measure':                  [':MEAS?', lambda s: float(s)],

    'clear_log':                [':SYST:CLEAR'],
    'system_error_next':        [':SYST:ERR:NEXT?', lambda s: _parse_log_event(s)],

    'clear_user_screen':        [':DISP:CLEAR'],
    'display_user_text':        [lambda line, text: f':DISP:USER{line}:TEXT "{text}"',
                                 lambda line: line if line in {1, 2} else None,
                                 lambda text: str(text)],

    # simple queries
    'detected_line_frequency':  [':SYST:LFR?', float],

    # setting of settings
    'set_function':             [':SENS:FUNC "{0}"', lambda val: str(val) if str(val) in list(map(str, Function)) else None],
    'set_screen':               [':DISP:SCREEN {0}', lambda val: str(val) if str(val) in list(map(str, Screen)) else None],

    'set_range':                [lambda v, mm_func: f':SENS:{mm_func}:RANG {v}' if v != 'auto' else f':SENS:{mm_func}:RANG:AUTO ON',
                                 lambda val: val if val == 'auto' or isinstance(val, (float, int)) else None],
}

sense_queries = {
    'set_auto_zero':            ['AZER {0}', lambda val: {False: 'OFF', True: 'ON'}.get(val, None)],
    'set_nplc':                 ['NPLC {0}', lambda val: float(val) if (0.0005 <= float(val) <= 12.0) else None],
}


def _sense_queries_transform(template):
    format_func = template[0]
    assert isinstance(format_func, str)
    return [':SENS:{mm_func}:' + format_func] + template[1:]


def _combined_queries(queries_templates,
                      _sense_queries):
    result = dict()
    result.update(queries_templates)
    result.update(dict((name, _sense_queries_transform(val)) for name, val in _sense_queries.items()))
    return result


def _parse_log_event(s):
    groups = re.fullmatch(r'([+\-\d]+),"(.+)"', s.strip()).groups()
    return int(groups[0]), groups[1]


def query_text(template, mm_state, values):
    formt = template[0]
    rest = template[1:]

    if isinstance(formt, Callable):
        param_info = inspect.signature(formt).parameters
        requires_mm_state = 'mm_func' in param_info
        no_required_args = len(param_info) - (1 if requires_mm_state else 0)
    else:
        requires_mm_state = formt.count('{mm_func}') == 1
        no_required_args = formt.count('{') - (1 if requires_mm_state else 0)

    parameter_convert_funcs = rest[:no_required_args]

    if no_required_args != len(values):
        raise ValueError

    if len(rest) > no_required_args:
        return_convert = rest[-1]
    else:
        return_convert = None

    query_type = 'write' if return_convert is None else 'query'

    converted_values = [f(v) for f, v in zip(parameter_convert_funcs, values)]
    if None in converted_values:
        raise ValueError

    if isinstance(formt, Callable):
        if requires_mm_state:
            return query_type, formt(*converted_values, mm_func=mm_state), return_convert
        else:
            return query_type, formt(*converted_values), return_convert
    else:
        return query_type, formt.format(*converted_values, mm_func=mm_state), return_convert


all_query_templates = _combined_queries(query_templates, sense_queries)