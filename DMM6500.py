from typing import Union

import pyvisa as visa

import DMM6500_SCPI


class DummyVisaResource:
    @staticmethod
    def write(txt):
        print(f'scpi write: {txt}')

    @staticmethod
    def query(txt):
        print(f'scpi query: {txt}')
        return ""


MMResourceType = Union[visa.Resource, DummyVisaResource]


class DMM6500:
    def __init__(self, resource: MMResourceType):
        self.r = resource
        self.last_selected_function = None

    def __setattr__(self, key: str, value):
        if key == 'function':
            self.last_selected_function = value

        set_query_name = f'set_{key}'
        if set_query_name in DMM6500_SCPI.all_query_templates:
            do_query(self.r, set_query_name, self.last_selected_function, [value])
        else:
            self.__dict__[key] = value

    def __getattr__(self, key: str):
        if key in DMM6500_SCPI.all_query_templates:
            return lambda *args: do_query(self.r, key, self.last_selected_function, args)

    def apply_settings(self, settings_dict: dict):
        if 'function' in settings_dict:
            self.__setattr__('function', settings_dict['function'])
            settings_dict.pop('function')

        for key, val in settings_dict.items():
            self.__setattr__(key, val)

    def get_all_errors(self):
        err = self.system_error_next()
        all_errors = []
        while err[0] != 0:
            all_errors.append(err)
            err = self.system_error_next()

        return all_errors


def do_query(r: MMResourceType, template_name, mm_state, args):
    method, cmd, return_convert = DMM6500_SCPI.query_text(DMM6500_SCPI.all_query_templates[template_name], mm_state, args)
    if method == 'write':
        r.write(cmd)
        return None
    elif method == 'query':
        convert = return_convert if return_convert is not None else lambda x: x
        return convert(r.query(cmd))
    else:
        assert False
