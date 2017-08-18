# -*- coding: utf-8 -*-
"""
    YSI Format Tests
    ~~~~~~~~~~~~~~~~

    These tests make sure that the YSI format module is working
    correctly
"""


import collections
import csv
from datetime import datetime
import os
import pytz

import nose
from nose.tools import assert_almost_equal, set_trace
import numpy as np
import quantities as pq

from sonde3 import sonde
#from sonde import quantities as sq
#from sonde.timezones import cdt, cst
#from sonde.formats import ysi


YSI_TEST_FILES_PATH = os.path.join(os.path.dirname(__file__), 'ysi_test_files')

cdt = pytz.timezone('US/Central')
utc=pytz.utc

def ysi_csv_read(filename):
    ysi_csv = collections.namedtuple('ysi_csv', 'dates, temps, spconds, depths, odos')

    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        # loop through first two header lines
        for i in range(2):
            next(csv_file)

        date_list = []
        temp_list = []
        spcond_list = []
        depth_list = []
        odo_list = []

        for row in csv_reader:
            timestamp = row[0] + ' ' + row[1]
            date = datetime.strptime(timestamp, '%m/%d/%y %H:%M:%S')
            #date = cdt.localize(date, is_dst=True).astimezone(utc)
            date_list.append(date)
            temp_list.append(row[2])
            spcond_list.append(row[3])
            depth_list.append(row[4])
            odo_list.append(row[5])

        ysi_csv.dates = np.array(date_list)
        ysi_csv.temps = np.array(temp_list)
        ysi_csv.spconds = np.array(spcond_list)
        ysi_csv.depths = np.array(depth_list)
        ysi_csv.odos = np.array(odo_list)

    return ysi_csv



def compare_quantity_and_csv_str(quantities, str_list):
    print (type(quantities))
    for quantity, string in list(zip(quantities, str_list)):
        #print (quantity, float(string))
        assert_almost_equal(float(quantity), float(string), places=1)





#-------------------------------------------------------------------
# Tests for ysi.YSIReader
#-------------------------------------------------------------------
class YSIReaderTestBase():
    def test_ysi_dates_match_csv(self):
        for date_pair in list(zip(self.ysi_reader['Datetime_(UTC)'], self.ysi_csv.dates)):
            
            if date_pair[1].tzinfo is not None:
                test_date = date_pair[1].replace(tzinfo=cdt).astimezone(utc)
            else:
                test_date = cdt.localize(date_pair[1], is_dst=True).astimezone(utc)
            assert date_pair[0] == test_date, "%r != %r" % (str(date_pair[0]), str(test_date))


class YSIReader_Test(YSIReaderTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        metadata, self.ysi_reader = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)
        self.ysi_csv = ysi_csv_read(csv_test_file_path)


class YSIReaderExplicitParamDef_Test(YSIReaderTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
        ysi_param_file_path = YSI_TEST_FILES_PATH + '/ysi_param.def'

        metadata, self.ysi_reader = sonde(ysi_test_file_path,  tzinfo=cdt, remove_invalids=False)
        self.ysi_csv = ysi_csv_read(csv_test_file_path)


def YSIReaderNaiveDatetime_Test():
    """
    Test that naive datetimes are allowed
    """
    ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
    
    metadata, ysi_reader = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)
    assert not ysi_reader.empty

#-------------------------------------------------------------------


class YSICompareWithCSVTestBase():
    def test_ysi_dates_match_csv(self):
        #print (self.ysi_dataset.head())
        for date_pair in list(zip(self.ysi_dataset['Datetime_(UTC)'], self.ysi_csv.dates)):
            if date_pair[1].tzinfo is not None:
                test_date = date_pair[1].replace(tzinfo=cdt).astimezone(utc)
            else:
                test_date = cdt.localize(date_pair[1], is_dst=True).astimezone(utc)
            assert date_pair[0] == test_date, "%r != %r" % (str(date_pair[0]), str(test_date))

    def test_ysi_temps_match_csv(self):
        compare_quantity_and_csv_str(self.ysi_dataset['water_temp_c'], self.ysi_csv.temps)

#    def test_ysi_spconds_match_csv(self):
#        compare_quantity_and_csv_str(self.ysi_dataset.data['water_specific_conductance'], self.ysi_csv.spconds)

    def test_ysi_depths_match_csv(self):
        compare_quantity_and_csv_str(self.ysi_dataset['water_depth_m_nonvented'], self.ysi_csv.depths)

    def test_ysi_odos_match_csv(self):
        compare_quantity_and_csv_str(self.ysi_dataset['water_DO_%'], self.ysi_csv.odos)


#-------------------------------------------------------------------
# Tests for sonde
#-------------------------------------------------------------------
class YSIDatasetFilePath_Test(YSICompareWithCSVTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        metadata, self.ysi_dataset = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)
        self.ysi_csv = ysi_csv_read(csv_test_file_path)
"""

class YSIDatasetFileObject_Test(YSICompareWithCSVTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        with open(ysi_test_file_path, 'rb') as fid:
            metadata, self.ysi_dataset = sonde(fid, tzinfo=cdt)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)
"""
"""
class YSIDatasetFileObject_Test(YSICompareWithCSVTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        with open(ysi_test_file_path, 'rb') as fid:
            metadata, self.ysi_dataset = sonde(fid, tzinfo=cdt)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)
"""

class YSIDatasetExplicitParamFile_Test(YSICompareWithCSVTestBase):
    """
    Test that data is read if param_def is explicitly specified
    """

    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
        ysi_param_file_path = YSI_TEST_FILES_PATH + '/ysi_param.def'

        metadata, self.ysi_dataset = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)


def YSIDatasetNaiveDatetime_Test():
    ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
    metadata, ysi_dataset = sonde(ysi_test_file_path)

    assert not ysi_dataset.empty


#-------------------------------------------------------------------
# Tests for the sonde object with a file_format='ysi'
#-------------------------------------------------------------------
class sondeYSIFormatFilePath_Test(YSICompareWithCSVTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        metadata, self.ysi_dataset = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)


"""
class sondeYSIFormatFileObject_Test(YSICompareWithCSVTestBase):
    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'

        with open(ysi_test_file_path, 'rb') as fid:
            metadata, self.ysi_dataset = sonde(fid, tzinfo=cdt)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)

"""

class sondeYSIExplicitParamFile_Test(YSICompareWithCSVTestBase):
    """
    Test that data is read if param_def is explicitly specified
    """

    def setup(self):
        csv_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.csv'
        ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
        ysi_param_file_path = YSI_TEST_FILES_PATH + '/ysi_param.def'

        metadata, self.ysi_dataset = sonde(ysi_test_file_path, tzinfo=cdt, remove_invalids=False)

        self.ysi_csv = ysi_csv_read(csv_test_file_path)


def sondeYSINaiveDatetime_Test():
    ysi_test_file_path = YSI_TEST_FILES_PATH + '/BAYT_20070323_CDT_YS1772AA_000.dat'
    metadata, ysi_dataset = sonde(ysi_test_file_path, remove_invalids=False)

    assert not ysi_dataset.empty


if __name__ == '__main__':
    nose.run()

