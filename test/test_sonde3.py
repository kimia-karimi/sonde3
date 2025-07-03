import sonde3
import pandas
import unittest
import sys
import os
import warnings

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

    
def directory_runner(self,directory, test_column):
    """
    method traverses a directory of files to open with sonde3.
    """
    for filename in os.listdir(directory):
        with self.subTest(filename=filename):
                
            f = os.path.join(directory, filename)
            f = open(f, 'rb')
            try:
                metadata, df = sonde3.sonde(f, twdbparams=True)
            except:
                f.close()
                self.fail(msg='failed on file %s' % filename)
            self.assertIn(test_column, df.columns)
            
class TestSonde_Single(unittest.TestCase):
    """
    Class to test a single file for development purposes
    
    """
    def test_aquatroll600(self):
        test_column = 'seawater_salinity'
        directory = "test/testfiles/aquatroll"
        filename = "OBB_TEST.csv"
        f = os.path.join(directory, filename)
        f = open(f, 'rb')
        try:
            metadata, df = sonde3.sonde(f, twdbparams=True)
        except:
            f.close()
            self.fail(msg='failed on file %s' % filename)
        self.assertIn(test_column, df.columns)            

class TestSonde_CheckBulkFiles(unittest.TestCase):
    
    #Tests a directory of files to see if the action does not specifically raise an error on each sonde file.
    #These are the three main manufacturers we need to actively support post 2022.
    
    @ignore_warnings
    def test_ysi(self):
        directory = "test/testfiles/ysi"
        directory_runner(self,directory, 'seawater_salinity')
    @ignore_warnings
    def test_aquatroll(self):
        directory = "test/testfiles/aquatroll"
        directory_runner(self,directory, 'seawater_salinity')
    @ignore_warnings
    def test_lowell(self):
        directory = "test/testfiles/lowell"
        directory_runner(self,directory, 'northward_water_velocity')
    @ignore_warnings
    def test_twdb(self):
        directory = "test/testfiles/twdb"
        directory_runner(self,directory, 'seawater_salinity')
    @ignore_warnings
    def test_txblend(self):
        directory = "test/testfiles/txblend"
        directory_runner(self,directory, 'txblend_salinity')


class TestSonde_autodetect_file(unittest.TestCase):
    """
    Testing if the autodetect functionality works.  Not all functions are supported.
    """
    @ignore_warnings
    def test_twdb(self):
        test_string = sonde3.autodetect("test/testfiles/twdb/NSAB-A.csv")
        self.assertEqual(test_string, 'twdb_coastal')
    @ignore_warnings
    def test_ysi_binary(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/SA08.dat")
        self.assertEqual(test_string, 'ysi_binary')
    @ignore_warnings
    def test_ysi_cdf(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/SA08.CDF")
        self.assertEqual(test_string, 'ysi_csv')
    @ignore_warnings
    def test_ysi_ascii(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/0917GEB.txt")
        self.assertEqual(test_string, 'ysi_text')       
    @ignore_warnings
    def test_ysi_exo(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/GE-SA-B_17H104157_090617_060000.csv")
        self.assertEqual(test_string, 'ysi_exo_csv')    
    @ignore_warnings
    def test_ysi_exo2(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(test_string, 'ysi_exo2_csv')    
    @ignore_warnings
    def test_ysi_exobackup(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/spotchecks-galveston-180618-081639.csv")
        self.assertEqual(test_string, 'ysi_exo_backup')    
    @ignore_warnings
    def test_lowell(self):
        test_string = sonde3.autodetect("test/testfiles/lowell/1603103_SAB_05122016.csv")
        self.assertEqual(test_string, 'lowell_csv')
    @ignore_warnings
    def test_aquatroll(self):
        test_string = sonde3.autodetect("test/testfiles/aquatroll/HydroVu_AquaTROLL__Baffin_Bay_-1031427_2023-08-15_14-14-09_Export.csv")
        self.assertEqual(test_string, 'insitu_csv')
    @ignore_warnings
    def test_espey(self):
        test_string = sonde3.autodetect("test/testfiles/espey/BZ3L_ALL.csv")
        self.assertEqual(test_string, 'espey_csv')
    @ignore_warnings
    def test_eureka(self):
        test_string = sonde3.autodetect("test/testfiles/eureka/JDM2_20060808_CDT_EU0312.csv")
        self.assertEqual(test_string, 'eureka_csv')
    @ignore_warnings
    def test_generic(self):
        test_string = sonde3.autodetect("test/testfiles/generic/test1.csv")
        self.assertEqual(test_string,  'generic_csv')
    @ignore_warnings
    def test_greenspan_csv(self):
        test_string = sonde3.autodetect("test/testfiles/greenspan/JDM4_20070410_CST_GS0638.csv")
        self.assertEqual(test_string,  'greenspan_csv')
    @ignore_warnings
    def test_greenspan_txt(self):
        test_string = sonde3.autodetect("test/testfiles/greenspan/JDM2_20060130_CST_GS0639.txt")
        self.assertEqual(test_string,   'unsupported_ascii')
    @ignore_warnings
    def test_greenspan_xls(self):
        test_string = sonde3.autodetect("test/testfiles/greenspan/JARD_20080416_CDT_GS9550.xls")
        self.assertEqual(test_string,   'greenspan_xls')
    @ignore_warnings
    def test_hydrolab_txt_a(self):
        test_string = sonde3.autodetect("test/testfiles/hydrolab/SANT_20070125_CST_HY0000_000.txt")
        self.assertEqual(test_string,  'hydrolab_csv')
    @ignore_warnings
    def test_hydrolab_txt_b(self):
        test_string = sonde3.autodetect("test/testfiles/hydrolab/SANT_20060213_CST_HY4077_000.txt")
        self.assertEqual(test_string,   'hydrolab_csv')
    @ignore_warnings
    def test_hydrotech(self):
        test_string = sonde3.autodetect("test/testfiles/hydrotech/0109CONT.csv")
        self.assertEqual(test_string,   'hydrotech_csv')
    @ignore_warnings
    def test_txblend(self):
        test_string = sonde3.autodetect("test/testfiles/txblend/txblend-Boli.csv")
        self.assertEqual(test_string,   'txblend_csv')
   
    
        
class TestSonde_sonde_filepointer(unittest.TestCase):
    """
    Specific file tests for each file for more extensive tests.  These files were previously problem files
    that needed extra tinking to get to function, so they are good examples of when things can go wrong with the 
    package.
    """ 
    @ignore_warnings
    def test_twdb(self):
        fid = open("test/testfiles/twdb/NSAB-A.csv", 'rb')
        first_row = [3.11,9.76213025988005,0.923,15.3982,16.5994,21.211]
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 53)
        for i in range(5):
            self.assertAlmostEqual(df.iloc[0][i+1], first_row[i])
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)
    @ignore_warnings
    def test_sonde_ysi_binary(self):
        fid = open("test/testfiles/ysi/SA08.dat", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 700)
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
    @ignore_warnings
    def test_sonde_ysi_cdf(self):
        fid = open("test/testfiles/ysi/SA08.CDF", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 700)
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)
        self.assertIn('water_dissolved_oxygen_concentration', df.columns)
        self.assertIn('water_dissolved_oxygen_percent_saturation', df.columns)
    @ignore_warnings
    def test_sonde_ysi_ascii(self):
        fid = open("test/testfiles/ysi/0917GEB.txt", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 1760) 
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn( 'instrument_battery_voltage', df.columns)
    @ignore_warnings
    def test_sonde_ysi_exo(self):
        fid = open("test/testfiles/ysi/GE-SA-B_17H104157_090617_060000.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 1955)      
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)
        self.assertIn('water_dissolved_oxygen_percent_saturation', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('water_dissolved_oxygen_concentration', df.columns)
    @ignore_warnings
    def test_sonde_ysi_exo2(self):
        fid = open("test/testfiles/ysi/EMBData_Retrieved10.3.2019.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 1775)
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
    @ignore_warnings
    def test_sonde_ysi_exobackup(self):
        fid = open("test/testfiles/ysi/spotchecks-galveston-180618-081639.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 32)    
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('water_dissolved_oxygen_percent_saturation', df.columns)
        self.assertIn( 'water_dissolved_oxygen_concentration', df.columns)
        self.assertIn('water_ph', df.columns)
        self.assertIn('water_bga_pe_rfu', df.columns)
        self.assertIn('chlorophyll_a_rfu', df.columns)
        self.assertIn('water_depth_nonvented', df.columns)
        self.assertIn('water_electrical_conductivity', df.columns)
        self.assertIn('water_specific_conductance', df.columns)
        self.assertIn('instrument_battery_voltage', df.columns)  
    @ignore_warnings
    def test_sonde_lowell(self):
        fid = open("test/testfiles/lowell/1603103_SAB_05122016.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 3026) 
        self.assertIn('northward_water_velocity' , df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
        self.assertIn('eastward_water_velocity', df.columns)
        self.assertIn('water_speed', df.columns)
        self.assertIn('water_bearing', df.columns) 
    @ignore_warnings
    def test_aquatroll(self):
        fid = open("test/testfiles/aquatroll/HydroVu_AquaTROLL__Baffin_Bay_-1031427_2023-08-15_14-14-09_Export.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 255)    
        self.assertIn('seawater_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        self.assertIn('water_temperature', df.columns)
    @ignore_warnings
    def test_txblend(self):
        fid = open("test/testfiles/txblend/txblend-Boli.csv", 'rb')
        metadata, df = sonde3.sonde(fid, twdbparams=True)
        self.assertEqual(len(df), 12419)    
        self.assertIn('txblend_salinity', df.columns)
        self.assertIn('Datetime_(UTC)', df.columns)
        
    
class TestSonde_dependencies(unittest.TestCase):
    """
    Tests the version of libraries expected and known to run correctly for this package.
    """
    @ignore_warnings
    def test_pandas_version(self):
        self.assertEqual(pandas.__version__, "2.2.3")
    @ignore_warnings
    def test_python(self):
        self.assertEqual(sys.version[:4], "3.11")

class TestSonde_DataManipulation(unittest.TestCase):   
    """
    Testing mathematical procedures that change values
    """
    @ignore_warnings
    def test_remove_invalids(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF")
        self.assertGreaterEqual(df['water_specific_conductivity_mS/cm'].min(), 0)  
    @ignore_warnings
    def test_preserve_invalids(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", remove_invalids=False)
        self.assertLess(df['water_specific_conductivity_mS/cm'].min(), 0)  
    @ignore_warnings
    def test_twdbparams_true(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", twdbparams=True)
        if 'water_dissolved_oxygen_percent_saturation' in df.columns:
            pass
        else:
            self.fail(m="column did not include TWDB specific parameter")
    @ignore_warnings
    def test_twdbparams_false(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", twdbparams=False)
        if 'water_dissolved_oxygen_percent_saturation' in df.columns:
            self.fail(m="column included wrong parameter name for twdbparams=False")
        else:
            pass
            
if __name__ == '__main__':
    unittest.main()
