import pandas as pd
from datetime import datetime
import pytz
import os
import io, itertools
import csv
import warnings
import ntpath

def read_hydrotech(hydrotech_file, tzinfo=None ,delim=None):
    """ Reads a proprietary format Hydrotech file



    """
    utc=pytz.utc 
    if tzinfo:
        localtime = tzinfo
    else:
        localtime = pytz.timezone('US/Central')
        warnings.warn("Info: No time zone was set for file, assuming records are recorded in CST" , stacklevel=2)

    package_directory = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')

    DF = pd.read_csv(hydrotech_file, sep=delim, parse_dates={'Datetime_(ascii)': [0,1]},\
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
            columns.append(i)
    k = 0
    for index, row in DF[1:2].iterrows():
        for i in row:
            columns[k] = (columns[k], i)
            k+=1
    columns[0] = "Datetime_(ascii)"
    DF.columns = columns
    DF = DF.drop(DF.index[:2])
    DF = pd.concat([DF, pd.to_datetime(DF['Datetime_(ascii)']).rename('Datetime_(Native)')], axis=1)
    
    #convert timezone to UTC and insert at front column
    DF.insert(0,'Datetime_(UTC)' ,  DF['Datetime_(Native)'].map(lambda x: x.replace(tzinfo=localtime).astimezone(utc)))
    DF = DF.drop('Datetime_(Native)', 1)
    DF = DF.drop('Datetime_(ascii)', 1)
    
    #drop all the odd informational rows at bottom of file
    for col in DF.columns:   
        submatch = DEFINITIONS[DEFINITIONS['parameter'].str.contains(col[0])]
        if submatch.empty:
            warnings.warn("Could not match parameter <%s> to definition file" %str(col) , stacklevel=2)
     
        if "Unnamed" not in col[1]:  #check for a null value in the units column
            match = submatch[submatch['unit'].str.contains(col[1])]
        else:
            DF = DF.rename(columns={col: str(submatch.iloc[0]['standard'])})
            
        if not match.empty:
                DF = DF.rename(columns={col: str(match.iloc[0]['standard'])})
                
    raw_metadata = pd.read_csv(hydrotech_file, sep=delim, header=None,nrows=10)
    metadata = pd.DataFrame(columns=('Manufacturer', 'Instrument_Serial_Number','Model','Station','Deployment_Setup_Time', \
                                     'Deployment_Start_Time', 'Deployment_Stop_Time','Filename'))
    metadata = metadata.append([{'Manufacturer' : 'Hydrotech'}])
    head, tail = ntpath.split(hydrotech_file)
    metadata = metadata.set_value([0], 'Filename' , tail)
    for i, row in raw_metadata[0:9].iterrows():
        if i == 0:
            metadata = metadata.set_value([0], 'Model',  row[0].split()[0])
            metadata = metadata.set_value([0], 'Instrument_Serial_Number',  row[0].split()[1])
        elif i == 1:
            metadata = metadata.set_value([0], 'Station',  row[0].split(' : ')[1])
        elif i == 2:
            metadata = metadata.set_value([0], 'Deployment_Setup_Time',  datetime.strptime(row[0].split(' : ')[1], '%m%d%y'))

    #now convert all data rows to floats...
    #move this to separate function if I have to do this more than for hydrotechs
    floater = lambda x: float(x)

    #split set
    dt_column = DF.iloc[:,0]
    data = DF.iloc[:,1:]
    data = data.applymap(floater)
    

    DF = pd.concat([dt_column,data], axis=1)

    return metadata, DF
