from datetime import datetime

import netcdftime as NCT


def get_time_converter(time):
    """
    reftime,time_converter = get_time_converter(time)
    *input:
    time = nc.variables['time'],
    where nc is a netCDF4.Dataset object
    *outputs:
    reftime - datetime.datetime object
    time_converter netCDF4.netcdftime.utime object
    """
    date_templates = [
        '%Y%m%dT%H%M%S',
        '%Y-%m-%dT%H%M%S',
        '%Y%m%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y%m%dT%H-%M-%S',
        '%Y-%m-%dT%H-%M-%S',
    ]

    tu        = time.units
    time_info = tu.split()

    # determine time format of reference point:
    unit = time_info[0]# 1st word gives units
    unit = unit.strip('s')
    if unit=='econd':
        unit = 'second'

    # try to match time info with strptime
    time_str_split = tu.replace('T', ' ').replace('Z', '').split()
    date_str = time_str_split[2] + 'T' + time_str_split[3]
    reftime = None
    for date_template in date_templates:
        try:
            reftime = datetime.strptime(date_str, date_template)
        except:
            pass
        else:
            break

    if reftime is None:
        raise ValueError('Unknown format of time in ', tu)

    init_string = reftime.strftime(f'{unit}s since %Y-%m-%d %H-%M-%S')

    if 'calendar' in time.ncattrs():
        time_converter = NCT.utime(init_string, calendar=time.calendar)
    else:
        time_converter = NCT.utime(init_string)

    return time_converter


def get_time_name(nc):
    """
    NEMO outputs call time "time_counter"
    CS2-SMOS thickness files use 'tc' for time dimension, but
    'time_bnds' for time variable
    """
    time_name = None
    for tname in [
            'time',
            'time0', #cfsr
            'time_counter',
            'time_bnds',
            ]:
        if tname in nc.dimensions:
            time_name = tname
            break

    return time_name

class BadAreaDefinition(Exception):
    """Exception raised for errors in the definition of area. This is a custom exception for
    development purposes. should not deal with the user. In the loop of finding a proper class for
    a netcdf file, this error cause the loop to go the next candidate class for instatiation.
    """
    pass
