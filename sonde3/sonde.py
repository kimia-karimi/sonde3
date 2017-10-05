from . import formats
import pandas as pd
import os
import seawater
import warnings




def sonde(filename, tzinfo=None, remove_invalids=True, twdbparams=False):
    """
    Convert an instrument file to pandas DataFrame

    Method autodetects the file type and calculates salinity (PSU) and dissolved oxygen (mg/L) if
    the required parameters are present
    """
    file_type = autodetect(filename)
    
    if file_type is 'ysi_binary':
        metadata, df = formats.read_ysi(filename, tzinfo)
    elif file_type is 'ysi_exo_csv':
        metadata, df = formats.read_ysi_exo_csv(filename)
    elif file_type is 'ysi_csv':
        metadata, df = formats.read_ysi_ascii(filename,  tzinfo,',',)
    elif file_type is 'ysi_csv_datetime':
        metadata, df = formats.read_ysi_ascii(filename,  tzinfo,',',[0])
    elif file_type is 'ysi_tab':
        metadata, df = formats.read_ysi_ascii(filename,  tzinfo,'\t')
    elif file_type is 'hydrotech_csv':
        metadata, df = formats.read_hydrotech(filename,  tzinfo,',') 
    else:
        warnings.warn("File format <%s> not supported in <%s>" %(str(file_type), str(filename)) , stacklevel=2)
        
        return pd.DataFrame(), pd.DataFrame()

    if not df.empty:
        if remove_invalids is True:
            df = _remove_invalids(df)

        df = calculate_conductance(df)
        df = calculate_salinity_psu(df)
        df = calculate_do_mgl(df)


        if twdbparams:
            #create a new index.  Pandas does not use mutable index's and
            #makes this a real pain.
            newcolumns = []
            for col in df.columns:
                if 'water_depth_m_nonvented' in col:
                    newcolumns.append('water_depth_nonvented')
                elif 'water_depth_m_vented' in col:    
                    newcolumns.append('water_depth_vented')
                elif 'water_specific_conductivity_mS/cm' in col:    
                    newcolumns.append(  'water_specific_conductance')
                elif 'water_conductivity_mS/cm' in col:    
                    newcolumns.append('water_electrical_conductivity')
                elif 'water_DO_mgl' in col:    
                    newcolumns.append(  'water_dissolved_oxygen_concentration')
                elif 'water_DO_%' in col:    
                    newcolumns.append('water_dissolved_oxygen_percent_saturation')
                elif 'water_temp_c' in col:    
                    newcolumns.append( 'water_temperature')
                elif 'water_salinity_PSU' in col:    
                    newcolumns.append('seawater_salinity' ) 
                elif 'water_turbidity_NTU' in col:    
                    newcolumns.append( 'water_turbidity')
                elif 'water_chorophyll-a_ug/L' in col:    
                    newcolumns.append( 'chlorophyll_a' )   
                else:
                    newcolumns.append(col)
                                        
            df.columns = newcolumns

    df = df.set_index(df['Datetime_(UTC)'])           
    return metadata, df


def _remove_invalids(df):
    #multiplies to remove negative values
    removezero = lambda x: x*(x>0)

    columns = ['water_depth_m_nonvented', 'water_conductivity_mS/cm', 'water_specific_conductivity_uS/cm'\
               'water_DO_%','water_specific_conductivity_mS/cm',  'water_conductivity_uS/cm']
    for column in columns:
        if column not in df.columns:
            continue
        df[column] = df[column].apply(removezero)
        
    return df

    

    
def calculate_conductance(df):
    """
    Calculates conductane or specific conductance depending on what is missing from the data
    """
    if ('water_conductivity_uS/cm' in df.columns):
        df['water_conductivity_mS/cm'] = df.apply (_scale_conductivity_us,axis=1)
        df = df.drop(['water_conductivity_uS/cm'],axis = 1)
    if ('water_specific_conductivity_uS/cm' in df.columns):
        df['water_specific_conductivity_mS/cm'] = df.apply (_scale_spconductivity_us,axis=1)
        df = df.drop(['water_specific_conductivity_uS/cm'],axis = 1)
        
    
    if ('water_conductivity_mS/cm' in df.columns) and ('water_specific_conductivity_mS/cm' in df.columns):
        return df
    elif ('water_conductivity_mS/cm' in df.columns) and ('water_temp_c' in df.columns) and not ('water_specific_conductivity_mS/cm' in df.columns):
        df['water_specific_conductivity_mS/cm'] = df.apply (_calculate_specific_conductivity,axis=1)
    elif ('water_specific_conductivity_mS/cm' in df.columns)  and ('water_temp_c' in df.columns) and not ('water_conductivity_mS/cm' in df.columns):
        df['water_conductivity_mS/cm'] = df.apply (_calculate_conductivity,axis=1)
    return df

def calculate_salinity_psu(df):
    """
    Calculate salinity PSU using UNESCO 1981 and UNESCO 1983 (EOS-80) via `seawater` package
    """
    if ('water_temp_c' in df.columns) and ('water_conductivity_mS/cm' in df.columns) and ('water_depth_m_nonvented' in df.columns):
        df['water_salinity_PSU'] = df.apply (_calculate_salinity_psu,axis=1)
    return df
        
def _calculate_salinity_psu(row):
    
    return  seawater.salt(row['water_conductivity_mS/cm']/ 42.914, row['water_temp_c'], row['water_depth_m_nonvented'] + 10.132501)

def _scale_conductivity_us(row):

    return (row['water_conductivity_uS/cm']/1000.0)

def _scale_spconductivity_us(row):

    return (row['water_specific_conductivity_uS/cm']/1000.0)
    
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

def _calculate_specific_conductivity(row):
    """ formula from https://in-situ.com/wp-content/uploads/2015/01/Specific-Conductance-as-an-Output-Unit-for-Conductivity-Readings-Tech-Note.pdf
    """
    r = 0.0191
    return  (row['water_conductivity_mS/cm']/ (1.0 + (r * (row['water_temp_c'] - 25.0))))

def _calculate_conductivity(row):
    """ formula from https://in-situ.com/wp-content/uploads/2015/01/Specific-Conductance-as-an-Output-Unit-for-Conductivity-Readings-Tech-Note.pdf
    """
    r = 0.0191
    return  (row['water_specific_conductivity_mS/cm'] * (1.0 + (r * (row['water_temp_c'] - 25.0))))
        
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

    
    if hasattr(filename, "read"):
        fid = filename
    else:
        fid = open(filename,  'rb')

    #is_binary_string(open(filename, 'rb').read(1024)):

        
    if is_binary_string(fid.read(1024)):
        fid.seek(0)
        lines = [fid.readline() for i in range(1000)]
        #lines = list(fid)
        #print (lines[0][0], lines[0])
        if lines[0].find(b'PDF') != -1:
            filetype =  'pdf'             
        if lines[0][0] == 65:
            filetype =  'ysi_binary'
        elif lines[0][0] == 'A':
            filetype =  'ysi_binary'
        elif lines[0].find(b'MacroCTD') != -1:
            filetype =  'macroctd_binary'
        elif lines[0].find(b'\x09\x08\x10\x00\x00\x06\x05\x00') != -1:  #xls types
            
            if lines[1].find(b'Manta') > -1 or lines[1].find(b'\xb0') > -1 or \
               lines[0].find(b'Start time : ') > -1:
                filetype = 'eureka_xls'
            elif (lines[0].find(b'Greenspan') != -1) or (lines[1].find(b'Greenspan') != -1) or (lines[0].find(b'GREENSPAN') != -1):
                filetype =  'greenspan_xls'
            else:
                if  lines[1].find(b'\xb0'):
                    filetype = 'eureka_xls'
                else:
                    filetype =  'unsupported_xls'
        else:
            if (lines[0].find(b',Greenspan') != -1):
                filetype = 'greenspan_xls'
            elif lines[2].find(b'Manta') > -1 or lines[1].find(b'\xb0') > -1 or \
                   lines[0].find(b'Start time : ') > -1:
                filetype = 'eureka_xls'
            elif(lines[0].find(b'\xdecgf') != -1):
                filetype = 'YSI_EXO'
            else:
                filetype = 'unsupported_bin'
    
        #fid.close()
    else:
        #fid = open(filename, 'r')
        fid.seek(0)
        
        #If fails we read an unsupported binary by mistake, so pass that to caller
        try:
            lines = [fid.readline() for i in range(3)]
        except:
            filetype =  'unsupported_binary'  
            return filetype
        
        
        if lines[0].lower().find(b'greenspan') != -1:
            filetype =  'greenspan_csv'
        elif lines[0].lower().find(b'minisonde') != -1:
            filetype =  'hydrotech_csv'
        elif lines[0].lower().find(b'log file name') != -1:
            filetype =  'hydrolab_csv'
        elif lines[0].lower().find(b'data file for datalogger.') != -1:
            filetype =  'solinst_csv'
        elif lines[0].find(b'Serial_number:')!= -1 and lines[2].find(b'Project ID:')!= -1:
            filetype = 'solinst_csv'
        elif lines[0].lower().find(b'pysonde csv format') != -1:
            filetype =  'generic_csv'
        elif lines[0].find(b'espey') != -1:
            filetype =  'espey_csv'
        elif lines[0].lower().find(b'request date') != -1:
            filetype =  'midgewater_csv'
        elif lines[0].find(b'the following data have been') != -1:
            filetype =  'lcra_csv'
        elif lines[0].find(b'=') != -1:
            filetype =  'ysi_text'
        elif lines[0].find(b'##YSI ASCII Datafile=') != -1:
            filetype =  'ysi_ascii'
        elif (lines[0].find(b"Date") > -1 )and (lines[1].find(b"M/D/Y") > -1 )and (lines[0].find(b"\t") > -1):
            filetype =  'ysi_tab'
        elif lines[0].find(b"DateTime") > -1 and lines[1].find(b"M/D/Y") > -1 and lines[0].find(b","):
            filetype =  'ysi_csv_datetime'
        elif lines[0].find(b"Date") > -1 and lines[1].find(b"M/D/Y") > -1 and lines[0].find(b","):
            filetype =  'ysi_csv'
        elif lines[0].find(b"Date") > -1 and lines[1].find(b"Y/M/D") > -1 and lines[0].find(b","):
            filetype =  'ysi_csv'
        elif lines[2].find(b'Manta') > -1 or lines[1].find(b'\xb0') > -1 or \
           lines[0].find(b'Start time : ') > -1:
            filetype = 'eureka_csv'
        elif lines[0].lower().find(b'macroctd') != -1:
            filetype = 'macroctd_csv'
        elif lines[0].lower().find(b'kor export file') != -1:
            filetype = 'ysi_exo_csv'
            
        else:
            filetype = 'unsupported_ascii'
            
    #fid.close()
    return filetype
        
