
import warnings


def match_param(DF,DEFINITIONS):
    """
    Method tries to match the columns of a dataframe to the definitions file sonde3/data/definitions.csv
    
    If the column cannot be matched a warnings.warn is passed.
    
    """
    for col in DF.columns:
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
            
    return DF
   
