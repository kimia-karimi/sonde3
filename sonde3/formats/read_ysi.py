import struct 
import pandas as pd
from datetime import datetime
import pytz
import os
import io, itertools
import csv
import warnings
import time
import six
import ntpath
from .utils import match_param

def read_ysi(ysi_file, tzinfo=None):
        """
        Read a proprietary YSI sonde instrument file returning as a `pandas` dataframe in UTC timezone
        
        Author: evan.turner@twdb.texas.gov 2017/07/20
        YSI sonde files are 8-bit byte binary files comprised of three sections that appear in order: 
        1. File metadata
            * fixed size of file/instrument specific metadata like serial numbers and site in format
            '<HLH16s32s6sLll36s'
        2. Sensor and parameter metadata
            * variable number of rows of fixed column sizes describing the sensors and units.  In format
            ''<hhHff' This is then translated via the YSI_DEFINITIONS file into human readable header names
            for the data columns.
        3. Data rows 
            * variable number of rows of data.  In format '<l' + str(number of parameters) + 'f' 
            Column lengths dependent on how many sensor parameter rows were previously encountered 
            in the previous section of the file.
        
        Datetime Considerations
        The datetime format for YSI is seconds since the 'YSI_epoch' which began march 1, 1984!? Making assumption it was EST?
        YSI files include no timezone or GPS information.  Therefore, without passing a timezone structure we must assume
        the instrument recorded data somewhere in the continental USA.
        
        Data Considerations
        Salinity and DO mg/L are calculated in the YSI handset, or the YSI windows program.  The raw binary file either does 
        not include this (salinity), or reports the sensor mvolts or intermediary constant (in case of DO).  Therefore, this
        has to be post-processed after reading the binary file.
        
        :param ysi_file: filename of YSI binary *.dat file
        :type ysi_file: String
        :param tzinfo: Expected timezone of file
        :type tzinfo: `datetime.tzinfo`
        :returns:  `pandas.DataFrame`, `Pandas.DataFrame`    
        """
        if hasattr(ysi_file, "read"):
            fid = ysi_file
            fid.seek(0)
        else:
            try:
                fid = open(ysi_file, 'rb')
            except:
                print("Error: Could not open file <%s> \n" % ysi_file)
                raise
      
        
        
        utc=pytz.utc 
        if tzinfo:
            localtime = tzinfo
        else:
            localtime = pytz.timezone('US/Central')

            warnings.warn("Info: No time zone was set for file, assuming records are recorded in CST" , stacklevel=2)
        package_directory = os.path.dirname(os.path.abspath(__file__))
        YSI_DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/ysi_definitions.csv"))
        DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')
        
        record_type = []
        num_params = 0
        data = []
        parameters = [] 
        parameters.append("Datetime_(UTC)")
        ysi_epoch = datetime(year=1984, month=3, day=1, tzinfo=pytz.timezone('US/Eastern'))
        ysi_epoch_in_seconds = time.mktime(ysi_epoch.timetuple())
        record_type = fid.read(1)  #read single 8-bit byte
        while record_type:
            if record_type == b'A':  #sonde file metadata
                fmt = '<HLH16s32s6sLll36s'  #little endian: uint,ulong,uint,16char,32char,6char,ulong,long,long,36char
                fmt_size = struct.calcsize(fmt)
                instr_type, system_sig, prog_ver, \
                                 serial_number, site_name, \
                                 pad1, logging_interval, \
                                 begin_log_time, \
                                 first_sample_time, pad2 \
                                 = struct.unpack(fmt, fid.read(fmt_size))
                                    
                #convert time variables into UTC, and cleanup binary format to UTF8                    
                first_sample_time = datetime.fromtimestamp(first_sample_time + ysi_epoch_in_seconds)\
                                    .replace(tzinfo=localtime).astimezone(utc)
                begin_log_time = datetime.fromtimestamp(begin_log_time + ysi_epoch_in_seconds)\
                                .replace(tzinfo=localtime).astimezone(utc)
                site_name = site_name.strip(b'\x00').decode("utf-8") 
                serial_number = serial_number.strip(b'\x00').decode("utf-8") 
                
                metadata = pd.DataFrame([(instr_type,"YSI",serial_number,site_name, \
                                        "")], columns=['Model', 'Manufacturer', \
                                        'Instrument_Serial_Number','Station', \
                                        'Deployment_Setup_Time'])
                
                if hasattr(ysi_file, "__getitem__"):
                        head, tail = ntpath.split(ysi_file)
                        metadata = metadata.set_value([0], 'Filename' , tail)
                else:
                        metadata = metadata.set_value([0], 'Filename' , ysi_file.filename)
                        
            elif record_type == b'B':  #row headers of the data
                num_params = num_params + 1
                fmt = '<hhHff'  #little endian: short,short,ushort,float,float
                fmt_size = struct.calcsize(fmt) 
                channel, sensor,probe,zero_scale,full_scale = struct.unpack(fmt, fid.read(fmt_size))
                parameters.append(YSI_DEFINITIONS.loc[sensor]["Short_Name"] )

                #check master definition list to see if parameter is verified
                submatch = DEFINITIONS[DEFINITIONS['standard'].str.contains(parameters[-1])]
                if submatch.empty:
                    warnings.warn("<%s> Could not match parameter <%s> to definition file" % (str(metadata['Filename'])  ,str(parameters[-1])) , stacklevel=2)
            elif record_type == b'D':  #actual data rows
                fmt = '<l' + str(num_params) + 'f'  #little endian, long (our datetime), variable number floats (our data rows)
                fmt_size = struct.calcsize(fmt)
                while record_type == b'D':  #repeat importing rows until EOF
                    row = list(struct.unpack(fmt, fid.read(fmt_size)))
                    dt = datetime.fromtimestamp(row[0] + ysi_epoch_in_seconds)
                    dt_dst = localtime.localize(dt, is_dst=True)
                    #row[0] = dt.astimezone(utc)
                    
                    if bool(dt_dst.dst()):
                        dt = datetime.fromtimestamp(row[0] + ysi_epoch_in_seconds - 3600)
                        row[0] = localtime.localize(dt, is_dst=True).astimezone(utc)
                    else:
                        #dt = datetime.fromtimestamp(row[0] + ysi_epoch_in_seconds)
                        row[0] = dt_dst.astimezone(utc)
                    
                    data.append(row)
                    record_type = fid.read(1) 
                #the file has ended, close and return    
                fid.close()
                DF = pd.DataFrame.from_records(data, columns=parameters)
                metadata['Deployment_Start_Time'] = DF['Datetime_(UTC)'].iloc[0]
                metadata['Deployment_Stop_Time'] = DF['Datetime_(UTC)'].iloc[-1]
                return metadata, DF
            
            else:        
                print('Error: Unknown binary formatting found in: <%s>' % ysi_file)
                break
                
            record_type = fid.read(1)

        #something went wrong with file parsing, close and return
        fid.close()
        warnings.warn ("Warning: binary read parsing error in file <%s> \n File may not be complete." % ysi_file, stacklevel=2)

        return metadata, pd.DataFrame.from_records(data, columns=parameters)


def read_ysi_ascii(ysi_file, tzinfo=None ,delim=None, datetimecols=None, header=None):
    """
    Method reads a text based YSI sonde instrument file and returns a pandas DataFrame for the table and metadata.

    Method makes many assumptions about the standard formatting of the text file.
    Method assumes the file is of YSI origin, has at least two columns.

    A separator must be passed to the function as the deliminator YSI uses
    can be different.  (Somtimes tab separated, comma, or a series of spaces)

    The function assumes that ['date','time'] are in column 0 and 1.  However, passing the index for datetimecols will
    allow the support of alternate datetime parsing with pandas.
    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS = pd.read_csv(os.path.join(package_directory,'..',"data/definitions.csv"), encoding='cp1252')

    utc=pytz.utc 
    if tzinfo:
        localtime = tzinfo
    else:
        localtime = pytz.timezone('US/Central')
        warnings.warn("Info: No time zone was set for file, assuming records are recorded in CST" , stacklevel=2)

    if datetimecols is None:
        datetimecols = [0,1]
        
    if header is None:
        header = [0,1]
    if not isinstance(ysi_file, six.string_types):
        ysi_file.seek(0)    
    DF = pd.read_csv(ysi_file,parse_dates={'Datetime_(Native)': datetimecols}, sep=delim, engine='python', header=header,na_values=['','na'])
    
    #print (DF.columns)   
    fixed_columns = []
    for col in DF.columns:
        if len(col) > 2: 
            #print ("found --")
            a = ''.join(col).rstrip("-")
            a = ''.join(a).lstrip(" ")
            fixed_columns.append(a)
        else:
            fixed_columns.append(col)
    DF.columns = fixed_columns
    DF.reindex(columns = fixed_columns)  
    
    #convert timezone to UTC and insert at front column
    DF.insert(0,'Datetime_(UTC)' ,  DF['Datetime_(Native)'].map(lambda x: localtime.localize(x).astimezone(utc)))
    DF = DF.drop('Datetime_(Native)', 1)

    
    #this submethod will match our read columns (tuple) to the master DEFINITION file
    """for col in DF.columns:
        #print "matching col:", col
        if 'Datetime_(UTC)' in col:
            continue
        param = col.split()
        
        submatch = DEFINITIONS[DEFINITIONS['parameter'].str.contains(param[0])]
               
        if "Unnamed" not in col[1]:  #check for a null value in the units column
            match = submatch[submatch['unit'].str.contains(param[1])]
            
        else:
            DF = DF.rename(columns={col: str(submatch.iloc[0]['standard'])})
            print (str(submatch.iloc[0]['standard']))
            
        if not match.empty:
            DF = DF.rename(columns={col: str(match.iloc[0]['standard'])})
            #print (str(match.iloc[0]['standard']))
        else:
            warnings.warn("Could not match parameter <%s> to definition file" %str(col) , stacklevel=2)
    """
    DF = match_param(DF,DEFINITIONS)        


    #create metadata
    metadata =  pd.DataFrame(data = [['YSI', '', '', '', '', '', '']], columns=['Manufacturer', 'Instrument_Serial_Number','Model', \
                                                                                'Station', 'Deployment_Setup_Time', 'Deployment_Start_Time', \
                                                                                'Deployment_Stop_Time'])
    #head, tail = ntpath.split(ysi_file)
    #metadata = metadata.set_value([0], 'Filename' , tail)
    metadata['Deployment_Start_Time'] = DF['Datetime_(UTC)'].iloc[0]
    metadata['Deployment_Stop_Time'] = DF['Datetime_(UTC)'].iloc[-1]
    
    return metadata, DF
