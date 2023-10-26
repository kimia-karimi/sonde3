import sonde3
import pandas
import unittest
import sys
import os

def directory_runner(self,directory, record_length, ftype):
    """
    method traverses a directory of files to open with sonde3.
    """
    for filename in os.listdir(directory):
        with self.subTest(filename=filename):
                
            f = os.path.join(directory, filename)
            if ftype == 'pointer':
                f = open(f, 'rb')
            try:
                metadata, df = sonde3.sonde(f)
            except:
                self.fail(msg='failed on file %s' % filename)
            self.assertGreaterEqual(len(df), record_length)
            if ftype == 'pointer':
                f.close()
            
            

class TestSonde_CheckBulkFiles(unittest.TestCase):
    """
    Tests a directory of files to see if the action does not specifically raise an error on each sonde file.
    These are the three main manufacturers we need to actively support post 2022.
    """
    def test_ysi(self):
        directory = "test/testfiles/ysi"
        directory_runner(self,directory,32,"file")
    def test_aquatroll(self):
        directory = "test/testfiles/aquatroll"
        directory_runner(self,directory,100,"file")
    def test_lowell(self):
        directory = "test/testfiles/lowell"
        directory_runner(self,directory,300,"file")
    
class TestSonde_CheckBulkPointers(unittest.TestCase):
    """
    Tests a directory of files to see if the action does not specifically raise an error on each sonde file pointer.
    These are the three main manufacturers we need to actively support post 2022.
    """
    def test_ysi(self):
        directory = "test/testfiles/ysi"
        directory_runner(self,directory,32,"pointer")
    def test_aquatroll(self):
        directory = "test/testfiles/aquatroll"
        directory_runner(self,directory,100,"pointer")
    def test_lowell(self):
        directory = "test/testfiles/lowell"
        directory_runner(self,directory,300,"pointer")    

class TestSonde_autodetect_file(unittest.TestCase):
 
    def test_ysi_binary(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/SA08.dat")
        self.assertEqual(test_string, 'ysi_binary')
    def test_ysi_cdf(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/SA08.CDF")
        self.assertEqual(test_string, 'ysi_csv')
    def test_ysi_ascii(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/0917GEB.txt")
        self.assertEqual(test_string, 'ysi_text')       
    def test_ysi_exo(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/GE-SA-B_17H104157_090617_060000.csv")
        self.assertEqual(test_string, 'ysi_exo_csv')    
    def test_ysi_exo2(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(test_string, 'ysi_exo2_csv')    
    def test_ysi_exobackup(self):
        test_string = sonde3.autodetect("test/testfiles/ysi/spotchecks-galveston-180618-081639.csv")
        self.assertEqual(test_string, 'ysi_exo_backup')    
    def test_lowell(self):
        test_string = sonde3.autodetect("test/testfiles/lowell/1603103_SAB_05122016.csv")
        self.assertEqual(test_string, 'lowell_csv')
    def test_aquatroll(self):
        test_string = sonde3.autodetect("test/testfiles/aquatroll/HydroVu_AquaTROLL__Baffin_Bay_-1031427_2023-08-15_14-14-09_Export.csv")
        self.assertEqual(test_string, 'insitu_csv')
    def test_espey(self):
        test_string = sonde3.autodetect("test/testfiles/espey/BZ3L_ALL.csv")
        self.assertEqual(test_string, 'espey_csv')
    def test_eureka(self):
        test_string = sonde3.autodetect("test/testfiles/eureka/JDM2_20060808_CDT_EU0312.csv")
        self.assertEqual(test_string, 'eureka_csv')
    def test_generic(self):
        test_string = sonde3.autodetect("test/testfiles/generic/test1.csv")
        self.assertEqual(test_string,  'generic_csv')
    def test_greenspan_csv(self):
        test_string = sonde3.autodetect("test/testfiles/greenspans/JDM4_20070410_CST_GS0638.csv")
        self.assertEqual(test_string,  'greenspan_csv')
    def test_greenspan_txt(self):
        test_string = sonde3.autodetect("test/testfiles/greenspan/JDM2_20060130_CST_GS0639.txt")
        self.assertEqual(test_string,   'unsupported_ascii')
    def test_greenspan_xls(self):
        test_string = sonde3.autodetect("test/testfiles/greenspan/JARD_20080416_CDT_GS9550.xls")
        self.assertEqual(test_string,   'greenspan_xls')
    def test_hydrolab_txt_a(self):
        test_string = sonde3.autodetect("test/testfiles/hydrolab/SANT_20070125_CST_HY0000_000.txt")
        self.assertEqual(test_string,  'hydrolab_csv')
    def test_hydrolab_txt_b(self):
        test_string = sonde3.autodetect("test/testfiles/hydrolab/SANT_20060213_CST_HY4077_000.txt")
        self.assertEqual(test_string,   'hydrolab_csv')
    def test_hydrotech(self):
        test_string = sonde3.autodetect("test/testfiles/hydrotech/0109CONT.csv")
        self.assertEqual(test_string,   'hydrotech_csv')
   
    
        

class TestSonde_sonde_filehandle(unittest.TestCase):
    """
    Specific file tests for each method to make sure sonde3 returns the exact number of rows for the file.
    This speficic class tests a file to be handed to the library, as you would be running it individually as a 
    stand-alone product.
    """
   
    def test_sonde_ysi_binary(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/SA08.dat")
        self.assertEqual(len(df), 700)
    def test_sonde_ysi_cdf(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/SA08.CDF")
        self.assertEqual(len(df), 700)
    def test_sonde_ysi_ascii(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/0917GEB.txt")
        self.assertEqual(len(df), 1760)        
    def test_sonde_ysi_exo(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/GE-SA-B_17H104157_090617_060000.csv")
        self.assertEqual(len(df), 1955)    
    def test_sonde_ysi_exo2(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(len(df), 1775)    
    def test_sonde_ysi_exobackup(self):
        metadata, df = sonde3.sonde("test/testfiles/ysi/spotchecks-galveston-180618-081639.csv")
        self.assertEqual(len(df), 32)    
    def test_sonde_lowell(self):
        metadata, df = sonde3.sonde("test/testfiles/lowell/1603103_SAB_05122016.csv")
        self.assertEqual(len(df), 3026)  
               

class TestSonde_sonde_filepointer(unittest.TestCase):
    """
    Specific file tests for each method to make sure sonde3 returns the exact number of rows for the file.
    This speficic class tests a filepointer to be passed to sonde3, as it would be for the WDFT package.
    """
    def test_sonde_ysi_binary(self):
        fid = open("test/testfiles/ysi/SA08.dat", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 700)
        fid.close
    def test_sonde_ysi_cdf(self):
        fid = open("test/testfiles/ysi/SA08.CDF", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 700)
        fid.close
    def test_sonde_ysi_ascii(self):
        fid = open("test/testfiles/ysi/0917GEB.txt", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 1760) 
        fid.close
    def test_sonde_ysi_exo(self):
        fid = open("test/testfiles/ysi/GE-SA-B_17H104157_090617_060000.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 1955)  
        fid.close
    def test_sonde_ysi_exo2(self):
        fid = open("test/testfiles/ysi/EMBData_Retrieved10.3.2019.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 1775)
        fid.close()
    def test_sonde_ysi_exobackup(self):
        fid = open("test/testfiles/ysi/spotchecks-galveston-180618-081639.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 32)    
        fid.close()
    def test_sonde_lowell(self):
        fid = open("test/testfiles/lowell/1603103_SAB_05122016.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 3026)  
        fid.close()
      
    
class TestSonde_dependencies(unittest.TestCase):
    """
    Tests the version of libraries expected and known to run correctly for this package.
    """
    def test_pandas_version(self):
        self.assertEqual(pandas.__version__, "0.25.3")
    def test_python(self):
        self.assertEqual(sys.version[:5], "3.6.8")

class TestSonde_DataManipulation(unittest.TestCase):   
    """
    Testing mathematical procedures that change values
    """
    def test_remove_invalids(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF")
        self.assertGreaterEqual(df['water_specific_conductivity_mS/cm'].min(), 0)  
    def test_preserve_invalids(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", remove_invalids=False)
        self.assertLess(df['water_specific_conductivity_mS/cm'].min(), 0)  
    def test_twdbparams_true(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", twdbparams=True)
        if 'water_dissolved_oxygen_percent_saturation' in df.columns:
            pass
        else:
            self.fail(m="column did not include TWDB specific parameter")
    def test_twdbparams_false(self):
        metadata, df = sonde3.sonde("test/testfiles/behaviortesting/negative-values.CDF", twdbparams=False)
        if 'water_dissolved_oxygen_percent_saturation' in df.columns:
            self.fail(m="column included wrong parameter name for twdbparams=False")
        else:
            pass
            
if __name__ == '__main__':
    unittest.main()