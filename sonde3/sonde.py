from . import formats
import pandas as pd
import os
import seawater




def sonde(filename, tzinfo=None):
    """
    Convert an instrument file to pandas DataFrame

    Method autodetects the file type and calculates salinity (PSU) and dissolved oxygen (mg/L) if
    the required parameters are present
    """
    file_type = autodetect(filename)
    
    if file_type is 'ysi_binary':
        metadata, df = formats.read_ysi(filename, tzinfo)
    elif file_type is 'ysi_csv':
        metadata, df = formats.read_ysi_ascii(filename,  tzinfo,',',)
    elif file_type is 'ysi_tab':
        metadata, df = formats.read_ysi_ascii(filename,  tzinfo,'\t',) 
    else:
        return pd.DataFrame(), pd.DataFrame()

    if not df.empty:
        df = calculate_salinity_psu(df)
        df = calculate_do_mgl(df)
        return metadata, df

def calculate_salinity_psu(df):
    """
    Calculate salinity PSU using UNESCO 1981 and UNESCO 1983 (EOS-80) via `seawater` package
    """
    if ('water_temp_c' in df.columns) and ('water_conductivity_mS/cm' in df.columns) and ('water_depth_m_nonvented' in df.columns):
        df['water_salinity_PSU'] = df.apply (_calculate_salinity_psu,axis=1)
    return df
        
def _calculate_salinity_psu(row):
    
    return  seawater.salt(row['water_conductivity_mS/cm']/ 42.914, row['water_temp_c'], row['water_depth_m_nonvented'] + 10.132501)
    
def calculate_do_mgl(df):
    """
    Calculate dissolved oxygen concentration in mg/L using Weiss's equation (1970).
    
    Weiss, R. (1970). "The solubility of nitrogen, oxygen, and argon in water and seawater".
    """
    if ('water_DO_%' in df.columns) and ('water_salinity_PSU' in df.columns) and ('water_temp_c' in df.columns):
        df['water_DO_mgl'] = df.apply (_calculate_do_mgl,axis=1)
    return df
        
def _calculate_do_mgl(row):
    tk = 1 / (row['water_temp_c'] + 273.15)
    p1 =-862194900000*tk**4+12438000000*tk**3-66423080*tk**2+157570.1*tk-139.344
    p2 =2140.7*tk**2-10.754*tk+0.017674
    dosat =0.01*2.71828182845904**(p1-row['water_salinity_PSU']*p2)
    return(row['water_DO_%'] * dosat)
              
def autodetect(filename):
    """
    Tests file for supported sonde filetypes.  
    
    This method may be slow due to the file pointer being opened and closed multiple times.  However, we only read at max 1024 bytes.
    """
    filetype = ''
    #test if file is binary or text.  This method does contain some false positives and negatives!
    # Will parse for those exceptions specifically where possible.
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    if is_binary_string(open(filename, 'rb').read(1024)):
        fid = open(filename, 'rb')
        lines = [fid.readline() for i in range(3)]
        if lines[0].find(b'PDF') != -1:
            filetype =  'pdf'             
        if lines[0][0] == 65:
            filetype =  'ysi_binary'
        elif lines[0].find(b'MacroCTD') != -1:
            filetype =  'macroctd_binary'
        elif lines[0].find(b'\x09\x08\x10\x00\x00\x06\x05\x00') != -1:  #xls types
            if lines[1].find(b'Manta') > -1:
                filetype = 'eureka_xls'
            elif (lines[0].find(b'Greenspan') != -1) or (lines[1].find(b'Greenspan') != -1) or (lines[0].find(b'GREENSPAN') != -1):
                filetype =  'greenspan_xls'
            else:
                filetype =  'unsupported_xls'
        else:
            if (lines[0].find(b',Greenspan') != -1):
                filetype = 'greenspan_csv'
            else:
                filetype = 'unsupported_csv'
    
        fid.close()
    else:
        fid = open(filename, 'r')
        
        #If fails we read an unsupported binary by mistake, so pass that to caller
        try:
            lines = [fid.readline() for i in range(3)]
        except:
            filetype =  'unsupported_binary'  
            fid.close()
            return filetype
        
        if lines[0].lower().find('greenspan') != -1:
            filetype =  'greenspan_csv'
        elif lines[0].lower().find('minisonde4a') != -1:
            filetype =  'hydrotech_csv'
        elif lines[0].lower().find('log file name') != -1:
            filetype =  'hydrolab_csv'
        elif lines[0].lower().find('data file for datalogger.') != -1:
            filetype =  'solinst_csv'
        elif lines[0].find('Serial_number:')!= -1 and lines[2].find('Project ID:')!= -1:
            filetype = 'solinst_csv'
        elif lines[0].lower().find('pysonde csv format') != -1:
            filetype =  'generic_csv'
        elif lines[0].find('espey') != -1:
            filetype =  'espey_csv'
        elif lines[0].lower().find('request date') != -1:
            filetype =  'midgewater_csv'
        elif lines[0].find('the following data have been') != -1:
            filetype =  'lcra_csv'
        elif lines[0].find('=') != -1:
            filetype =  'ysi_text'
        elif lines[0].find('##YSI ASCII Datafile=') != -1:
            filetype =  'ysi_ascii'
        elif (lines[0].find("Date") > -1 )and (lines[1].find("M/D/Y") > -1 )and (lines[0].find("\t") > -1):
            filetype =  'ysi_tab'
        elif lines[0].find("Date") > -1 and lines[1].find("M/D/Y") > -1 and lines[0].find(","):
            filetype =  'ysi_csv'
        elif lines[2].find('Manta') > -1:
            filetype = 'eureka_csv'
            
        else:
            filetype = 'unsupported_ascii'
            
    fid.close()
    return filetype
        
