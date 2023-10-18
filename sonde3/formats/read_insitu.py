import pandas as pd
from datetime import datetime
import pytz
import os
import io, itertools
import csv
import warnings
import six
import ntpath
from .utils import match_param

def read_insitu(aquatroll_file, tzinfo=None ,delim=None):
    """ Reads a proprietary format insitu file






    """
    #aquatroll data should be comma separated, we can force that here so package doesn't error with null
    if delim == None:
        delim = ','
  
    package_directory = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')
    utc=pytz.utc  #aquatroll files are always in UTC

    

    if not isinstance(aquatroll_file, six.string_types):
        aquatroll_file.seek(0)
    #grab 30 lines discover what the real header is, then trim the file
    raw_metadata = pd.read_csv(aquatroll_file, sep=delim, engine='c',na_values=['','na', 'NaN'],header=None, nrows=6)
    #header_row_index = raw_metadata.loc[raw_metadata[0].str.contains("Date")==True].index[0]
    #raw_metadata = raw_metadata.drop(raw_metadata.index[(header_row_index-2):])
    header_row_index = 8
    if not isinstance(aquatroll_file, six.string_types):
        aquatroll_file.seek(0)
    #grab main file from header point, squash datetime row
    DF = pd.read_csv(aquatroll_file, parse_dates={'Datetime_(UTC)': [0]}, sep=delim,na_values=['','na'], header = header_row_index)
    #DF = DF.drop(DF.index[:header_row_index])
    
    return DF