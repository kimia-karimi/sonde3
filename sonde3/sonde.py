from . import formats
import pandas as pd
import os

def sonde():
    print ("hi there")
    formats.read_ysi("test")

print ("running ./sonde3/sonde.py")
print (os.getcwd())

