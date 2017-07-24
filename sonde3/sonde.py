from . import formats
import pandas as pd
import os

def sonde():
    print ("hi there")
    formats.read_ysi("test")

def autodetect(filename):
    """
    Tests file for supported sonde filetypes.  
    
    This method may be slow due to the file pointer being opened and closed multiple times.

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
        lines = [fid.readline() for i in range(3)]
        
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
        elif lines[0].find("Date") > -1 and lines[1].find("M/D/Y") > -1:
            filetype =  'ysi_csv'
        elif lines[2].find('Manta') > -1:
            filetype = 'eureka_csv'
            
        else:
            filetype = 'unsupported_ascii'
            
    fid.close()
    return filetype
        
