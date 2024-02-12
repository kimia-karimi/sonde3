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

def read_txblend(txblend_file, tzinfo=None ,delim=None):
    """ Reads a proprietary format txblend file



    """
    
    utc=pytz.utc 
    if tzinfo:
        localtime = tzinfo
    else:
        localtime = pytz.timezone('US/Central')
        # txblend will always be in CST
        # warnings.warn("Info: No time zone was set for file, assuming records are recorded in CST" , stacklevel=2)

    package_directory = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')
    
    txblend_file.seek(0)
    DF = pd.read_csv(txblend_file, sep=delim, parse_dates={'Datetime_(ascii)': [0]},\
                      na_values=['','na', '999999', '#'], engine='c',encoding='cp1252', \
                      names = list(range(0,20)))

    #drop the end of the file messages if exist    
    droplist = ['Power loss', 'Late probe', 'Recovery finished']
    DF = DF[~DF['Datetime_(ascii)'].str.contains('|'.join(droplist))]

    #drop the null columns created by double deliminators
    DF = DF.dropna(how="all", axis=1)
    DF = DF.dropna(thresh=2)  # drop if we don't have at least 2 cells with real values

    columns = []
    for index, row in DF[0:1].iterrows():
        for i in row:
            columns.append(i.replace('(','').replace(')',''))
            
    k = 0
    '''for index, row in DF[1:2].iterrows():
        for i in row:
            columns[k] = (columns[k], i)
            k+=1
    '''
    columns[0] = "Datetime_(ascii)"
    DF.columns = columns
    DF = DF.drop(DF.index[:1])
    DF = pd.concat([DF, pd.to_datetime(DF['Datetime_(ascii)']).rename('Datetime_(Native)')], axis=1)
    
    #convert timezone to UTC and insert at front column
    DF.insert(0,'Datetime_(UTC)' ,  DF['Datetime_(Native)'].map(lambda x: x.replace(tzinfo=localtime).astimezone(utc)))
    DF = DF.drop('Datetime_(Native)', 1)
    DF = DF.drop('Datetime_(ascii)', 1)
    # drop all the odd informational rows at bottom of file

    # we don't need to match the parameters of the TXBLEND file
    #DF = match_param(DF,DEFINITIONS) 
   
    
    

    #now convert all data rows to floats...
    floater = lambda x: float(x)

    #split set
    dt_column = DF.iloc[:,0]
    data = DF.iloc[:,1:]
    data = data.applymap(floater)
    

    DF = pd.concat([dt_column,data], axis=1)

    txblend_file.close()
    DF.sort_index(inplace=True)
    
    return None, DF

