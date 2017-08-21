from datetime import datetime
import glob
import re

from configobj import ConfigObj
from nose.tools import assert_almost_equal, eq_, set_trace
import numpy as np
import quantities as pq
import pytz
import sonde3
#from sonde import quantities as sq
#from sonde.timezones import cst, cdt

# global tz
tz = None
cdt = pytz.timezone('US/Central')
cst = pytz.timezone('US/Central')
utc=pytz.utc


def test_files():
    test_config_paths = glob.glob('./*_test_files/*_test.txt')

    for test_config_path in test_config_paths:
        sonde_file_extension = test_config_path.split('_')[-2]
        sonde_file_base = test_config_path.rsplit('_' + sonde_file_extension,
                                                  1)[0]
        sonde_file_path = '.'.join([sonde_file_base,
                                    sonde_file_extension])

        test_file_config = ConfigObj(open(test_config_path), unrepr=True)

        yield check_autodetect, test_file_config, sonde_file_path

        yield check_file, test_file_config, sonde_file_path
"""
        with open(sonde_file_path) as sonde_file_fid:
            print('Testing:', sonde_file_path)
            yield check_file, test_file_config, sonde_file_fid
"""

def check_autodetect(test_file, sonde_file):
    file_format = test_file['header']['format']
    autodetect_result = sonde3.autodetect(sonde_file)

    assert autodetect_result == file_format, \
           "Autodetection failed: %s != %s" % (autodetect_result, file_format)


def check_file(test_file, sonde_file):
    global tz

    file_format = test_file['header']['format']

    # force cst, as the python naive datetime automatically converts
    # to cst which tends to screw things up
    if 'tz' in test_file['format_parameters']['tz'] and \
           test_file['format_parameters']['tz'].lower() == 'cdt':
        tz = cdt
    else:
        tz = cst
    print (sonde_file)
    test_sonde_metadata, test_sonde = sonde3.sonde(sonde_file, tzinfo=tz)
    check_format_parameters(test_file['format_parameters'], test_sonde_metadata)

    parameters = test_file['data']['parameters']
    units = test_file['data']['units']

    for test_data in test_file['data']['test_data']:
        check_values_match(test_data, parameters, units, test_sonde, test_sonde_metadata)


def check_values_match(test_data, parameters, units, test_sonde, metadata):
    date = _convert_to_aware_datetime(test_data[0])
    date = cdt.localize(date)
    #date = date.replace(tzinfo=cdt).astimezone(utc)
    date = date.astimezone(utc)
    if test_sonde.empty:
        assert test_sonde.empty is True, "Empty DataFrame"
        return

    assert 'Datetime_(UTC)' in test_sonde.columns, \
           "no datetime column in dataframe <%s>" %(test_sonde.columns)
        
    assert date in test_sonde['Datetime_(UTC)'].unique(), \
           "date <%s> not found in dataframe <%s>" % (date, metadata['Filename'])
    """
    for parameter, unit, test_value in zip(parameters, units, test_data[1:]):
        sonde_datum = test_sonde[parameter][test_sonde['Datetime_(UTC)'] == date]

        if unit in pq.__dict__:
            test_quantity = pq.__dict__[unit]
        elif unit in sq.__dict__:
            test_quantity = sq.__dict__[unit]
        else:
            raise "config error: could not find quantity for '%s '" % unit
        
        if test_value == 'nan':
            assert np.isnan(sonde_datum)
            continue

        #test_datum = (test_value * test_quantity).rescale(sonde_datum.units)
        test_datum = test_value
        # if value in the test file is less precise than the actual
        # data value, then just check the number of decimal places of
        # the test value. Note: this means trailing zeros ignored
        if len(str(test_value).split('.')) == 2:
            places = len(str(test_value).split('.')[1])
            print (test_datum, sonde_datum, places)
            assert_almost_equal(test_datum, sonde_datum, places)
        else:
            assert_almost_equal(test_datum, sonde_datum)
    """

def check_format_parameters(format_parameters, test_sonde):
    for parameter_name, test_value in list(format_parameters.items()):
        if test_value == '':
            continue

        if test_sonde.empty:
            assert test_sonde.empty, "empty DataFrame"
            return
        
        
        # parameters on the test_sonde object itself; historically, these
        # used to be in the format_parameters dict but now they are on
        # the test_sonde object and it's not worth the effort to rearrange
        # all the test files
        sonde_parameters = ['Instrument_Serial_Number', 'Station', 'Deployment_Setup_Time',
                            'Model', 'Manufacturer', 'Deployment_Start_Time', 'Deployment_Stop_Time']

        if parameter_name in sonde_parameters:
            assert hasattr(test_sonde, parameter_name), \
                   "format parameter '%s' not found in " \
                   "test_sonde" % parameter_name
            #sonde_parameter = getattr(test_sonde, parameter_name)

        else:
            assert parameter_name in test_sonde.columns, \
                   "format parameter '%s' not found in " \
                   "test_sonde.columns" % parameter_name
            #sonde_parameter = test_sonde.format_parameters[parameter_name]

        # if we are testing a datetime value
        if re.match('\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', test_value):
            test_value = _convert_to_aware_datetime(test_value)

        #assert test_value == sonde_parameter, \
        #       "format parameter '%s' doesn't match: '%s' != '%s'" % \
        #       (parameter_name, test_value, sonde_parameter)


def _tz_offset_string(tzinfo):
    """
    Return a tzoffset string in the form +HHMM or -HHMM as required
    for parsing the '%z' directive of the the datetime strptime()
    method's format for parsing datetime strings
    """
    offset = tzinfo.utcoffset(tzinfo)

    hours = offset.days * 24 + offset.seconds / 3600
    minutes = (offset.seconds % 3600) / 60

    return "%+03d%02d" % (hours, minutes)


def _convert_to_aware_datetime(datetime_string):
    """
    Convert to a datetime string to a datetime object, taking tz into
    account if it is set
    """
    date_format = "%m/%d/%Y %H:%M:%S"
    dt = datetime.strptime(datetime_string, date_format)

    #if tz:
    #    dt = dt.replace(tzinfo=tz)

    return dt
