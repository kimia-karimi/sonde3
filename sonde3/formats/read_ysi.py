import struct 
import pandas as pd
from datetime import datetime
import pytz
import os
import io, itertools
import csv

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
        try:
            fid = open(ysi_file, 'rb')
        except:
            print("Error: Could not open file <%s> \n" % ysi_file)
            raise
      
        YSI_DEFINITIONS = pd.read_csv("sonde3/data/ysi_definitions.csv")
        
        utc=pytz.utc 
        if tzinfo:
            localtime = tzinfo
        else:
            localtime = pytz.timezone('US/Central')
            print ("Info: No time zone was set for file, assuming records are recorded in CST")
            
        record_type = []
        num_params = 0
        data = []
        parameters = [] #3600 446965200
        parameters.append("datetime_(UTC)")
        ysi_epoch_in_seconds = 446962140 #time began for YSI on 2004/03/01 !!
        
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
                
                metadata = pd.DataFrame([(instr_type,"YSI",system_sig,prog_ver,serial_number,site_name,logging_interval,begin_log_time,
                                       first_sample_time)], columns=['Instrument_Type', 'Manufacturer', 'System_Signal',
                                        'Program_Version','Instrument_Serial_Number','Site','Logging_Interval',
                                        'Begin_Log_Time_(UTC)', 'First_Sample_Time_(UTC)'])
                
            elif record_type == b'B':  #row headers of the data
                num_params = num_params + 1
                fmt = '<hhHff'  #little endian: short,short,ushort,float,float
                fmt_size = struct.calcsize(fmt) 
                channel, sensor,probe,zero_scale,full_scale = struct.unpack(fmt, fid.read(fmt_size))
                parameters.append(YSI_DEFINITIONS.loc[sensor]["Short_Name"] )
            elif record_type == b'D':  #actual data rows
                fmt = '<l' + str(num_params) + 'f'  #little endian, long (our datetime), variable number floats (our data rows)
                fmt_size = struct.calcsize(fmt)
                while record_type == b'D':  #repeat importing rows until EOF
                    row = list(struct.unpack(fmt, fid.read(fmt_size)))
                    row[0] = datetime.fromtimestamp(row[0] + ysi_epoch_in_seconds)\
                            .replace(tzinfo=localtime).astimezone(utc)
                    data.append(row)
                    record_type = fid.read(1) 
                #the file has ended, close and return    
                fid.close()
                return metadata, pd.DataFrame.from_records(data, columns=parameters)
            
            else:        
                print('Error: Unknown binary formatting found in: <%s>' % ysi_file)
                break
                
            record_type = fid.read(1)

        #something went wrong with file parsing, close and return
        fid.close()
        print ("Warning: empty dataframe in file <%s>" % ysi_file)
        return metadata, pd.DataFrame.from_records(data, columns=parameters)


def read_ysi_ascii(ysi_file, sep, tzinfo=None):
    metadata =  pd.DataFrame(data = ['YSI'], columns=['Manufacturer'])
    DF = pd.read_csv(ysi_file,parse_dates={'datetime': [0,1]}, sep=sep, engine='python')
 
    header2 = DF.iloc[0]
    new_columns = []
    index = 0
    #combine first two rows into the header, strip offending " characters if needed
    for i in DF.columns:
        new_columns.append((str(i) + ' ' + str(header2[index])).replace('"',''))
        index +=1
    DF.columns = new_columns  
    return metadata, DF.drop(DF.index[0])
