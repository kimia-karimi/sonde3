import pandas as pd
from datetime import datetime
import pytz
import os
import io, itertools
import csv
import sys
import warnings
import six
import pytz
from .utils import match_param



#sv.field_size_limit(262144)  #setting to 256k  using sys.maxsize works on WDFT AWS prod, but crashes now with anaconda for windows

def read_twdb_coastal(twdb_file):
    """
    Method reads a text based YSI sonde instrument file in KOR >2.0 EXO format and returns a pandas DataFrame for the table and metadata.

    Method makes many assumptions about the standard formatting of the text file.
    Method assumes the file is of YSI origin, has at least two columns.

    A separator must be passed to the function as the deliminator YSI uses
    can be different.  (Somtimes tab separated, comma, or a series of spaces)

    The function assumes that ['date','time','fractime'] are in column 0 and 1 and 2.
    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    
    utc=pytz.utc

    twdb_file.seek(0)
    
    #determine the correct header row
    header_row_index = 3

    DF = pd.read_csv(twdb_file, engine='python', skip_blank_lines=False, parse_dates={'Datetime_(UTC)': [0]},na_values=[''], header = header_row_index)

    twdb_file.close()
    
   
    
    return None, DF
