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



csv.field_size_limit(262144)  #setting to 256k  using sys.maxsize works on WDFT AWS prod, but crashes now with anaconda for windows

def read_ysi_exo2_csv(ysi_file,delim=','):
    """
    Method reads a text based YSI sonde instrument file in KOR >2.0 EXO format and returns a pandas DataFrame for the table and metadata.

    Method makes many assumptions about the standard formatting of the text file.
    Method assumes the file is of YSI origin, has at least two columns.

    A separator must be passed to the function as the deliminator YSI uses
    can be different.  (Somtimes tab separated, comma, or a series of spaces)

    The function assumes that ['date','time','fractime'] are in column 0 and 1 and 2.
    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')

    utc=pytz.utc
    localtime = pytz.timezone('US/Central')

    ysi_file.seek(0)
    ysi_file_download = ysi_file.read().decode('ISO-8859-1')
   
    
    num = 0
 
    ysi_file_download = ysi_file_download.replace('\x00','')
    #ysi_file_download = ysi_file_download.replace('\r','\n')
    
    #determine the correct header row
    header_row_index = -1
    for i in ysi_file_download.splitlines(False):
        header_row_index+=1
       
        if 'Date' in i:
            break
    
    DF = pd.read_csv(io.StringIO(ysi_file_download), engine='python', skip_blank_lines=False, parse_dates={'Datetime_(Native)': [0,1]}, sep=delim,na_values=[''], header = header_row_index, encoding='utf-16')

    ysi_file.close()
    DF.insert(0,'Datetime_(UTC)' ,  DF['Datetime_(Native)'].map(lambda x: localtime.localize(x).astimezone(utc)))
    DF = DF.drop('Datetime_(Native)', axis=1)

    # stripping out all of the funky non-ascii characters out of the file so we can match properly
    # otherwise EXO degree mark will break the match algorithm
    new_cols = []
    for col in DF.columns:
        new_cols.append( ''.join(i for i in col if ord(i)<128))

    DF.columns = new_cols

    if 'Site' in DF:
        DF = DF.drop(columns=['Site'])
    if 'User ID' in DF:
        DF = DF.drop(columns=['User ID'])
    if 'Unit ID' in DF:
        DF = DF.drop(columns=['Unit ID'])
    if 'Time (Fract. Sec)' in DF:
        DF = DF.drop(columns=['Time (Fract. Sec)'])
        
    DF = match_param(DF,DEFINITIONS)
    
    
    return None, DF
