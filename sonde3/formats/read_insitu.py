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



   
    aquatroll_file.seek(0)
    #grab 30 lines discover what the real header is, then trim the file
    #raw_metadata = pd.read_csv(aquatroll_file, sep=delim, engine='python',na_values=['','na', 'NaN'],header=None, nrows=15, error_bad_lines=False)
    #file has odd number of columns, lets read a section for metadata to determine when we need to 'start' the full file:
    # import pdb;pdb.set_trace()
    # metadata = pd.read_csv(aquatroll_file, header=None, engine='c', sep='\n', nrows=9)
    lines = aquatroll_file.readlines()
    metadata_lines = lines[:9]
    metadata = pd.DataFrame([line.strip() for line in metadata_lines])

    header_row_index = 8 #will always be row 8 in aquatroll, which is very handy indead!
    


    
    aquatroll_file.seek(0)
    #grab main file from header point, squash datetime row
    DF = pd.read_csv(aquatroll_file, parse_dates={'Datetime_(UTC)': [0]}, sep=delim,na_values=['','na'], header = header_row_index, index_col=False)
    #DF = DF.drop(DF.index[:header_row_index])
    """
       Aquatroll files contain special formatting for the DO parameters that will break our entire package for definition conversion.
       Instead of completely redesigning the entire package at this point, this is a hold-over stop-gap to fix the issue indivisually
       for the parameters of our interest.  Then, we can pass back to the definition matcher for the rest.
    """
    columns = list(DF.columns)  #have to cast to list, otherwise error in non-mutable index.
    do_index = None
    spc_index = None
    charfu_index = None
    for idx, i in enumerate(columns):
        if "% Saturation" in i:
            do_index=idx
        if "Specific Conductivity" in i:
            spc_index = idx
        if "Chl-a Fluorescence" in i:
            charfu_index = idx

    if do_index is not None:
        columns[do_index] = "water_DO_%"
    if spc_index is not None:
        columns[spc_index] = "SpCond uS/cm"
    if charfu_index is not None:
        columns[charfu_index] = "Chlorophyll RFU"

    DF.columns = columns

    DF = match_param(DF,DEFINITIONS)
    aquatroll_file.close()
    return metadata, DF
