import sonde3
import pandas
import unittest
import sys


class TestSonde_autodetect_file(unittest.TestCase):
   
    def test_ysi_binary(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/SA08.dat")
        self.assertEqual(test_string, 'ysi_binary')
    def test_ysi_cdf(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/SA08.CDF")
        self.assertEqual(test_string, 'ysi_csv')
    def test_ysi_ascii(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/0917GEB.txt")
        self.assertEqual(test_string, 'ysi_text')       
    def test_ysi_exo(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/GE-SA-B_17H104157_090617_060000.csv")
        self.assertEqual(test_string, 'ysi_exo_csv')    
    def test_ysi_exo2(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(test_string, 'ysi_exo2_csv')    
    def test_ysi_exobackup(self):
        test_string = sonde3.autodetect("tests/ysi_test_files/spotchecks-galveston-180618-081639.csv")
        self.assertEqual(test_string, 'ysi_exo_backup')    
    def test_lowell(self):
        test_string = sonde3.autodetect("tests/lowell_test_files/1603103_SAB_05122016.csv")
        self.assertEqual(test_string, 'lowell_csv')
    def test_aquatroll(self):
        test_string = sonde3.autodetect("tests/aquatroll_test_files/HydroVu_AquaTROLL__Baffin_Bay_-1031427_2023-08-15_14-14-09_Export.csv")
        self.assertEqual(test_string, 'insitu_csv')
    def test_espey(self):
        test_string = sonde3.autodetect("tests/espey_test_files/BZ3L_ALL.csv")
        self.assertEqual(test_string, 'espey_csv')
    def test_eureka(self):
        test_string = sonde3.autodetect("tests/eureka_test_files/JDM2_20060808_CDT_EU0312.csv")
        self.assertEqual(test_string, 'eureka_csv')
    def test_generic(self):
        test_string = sonde3.autodetect("tests/generic_test_files/test1.csv")
        self.assertEqual(test_string,  'generic_csv')
    def test_greenspan_csv(self):
        test_string = sonde3.autodetect("tests/greenspan_test_files/JDM4_20070410_CST_GS0638.csv")
        self.assertEqual(test_string,  'greenspan_csv')
    def test_greenspan_txt(self):
        test_string = sonde3.autodetect("tests/greenspan_test_files/JDM2_20060130_CST_GS0639.txt")
        self.assertEqual(test_string,   'unsupported_ascii')
    def test_greenspan_xls(self):
        test_string = sonde3.autodetect("tests/greenspan_test_files/JARD_20080416_CDT_GS9550.xls")
        self.assertEqual(test_string,   'greenspan_xls')
    def test_hydrolab_txt_a(self):
        test_string = sonde3.autodetect("tests/hydrolab_test_files/SANT_20070125_CST_HY0000_000.txt")
        self.assertEqual(test_string,  'hydrolab_csv')
    def test_hydrolab_txt_b(self):
        test_string = sonde3.autodetect("tests/hydrolab_test_files/SANT_20060213_CST_HY4077_000.txt")
        self.assertEqual(test_string,   'hydrolab_csv')
    
        

class TestSonde_sonde_filehandle(unittest.TestCase):
    def test_pandas_version(self):
        self.assertEqual(pandas.__version__, "0.25.3")
    
    def test_sonde_ysi_binary(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/SA08.dat")
        self.assertEqual(len(df), 700)
    def test_sonde_ysi_cdf(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/SA08.CDF")
        self.assertEqual(len(df), 700)
    def test_sonde_ysi_ascii(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/0917GEB.txt")
        self.assertEqual(len(df), 1760)        
    def test_sonde_ysi_exo(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/GE-SA-B_17H104157_090617_060000.csv")
        self.assertEqual(len(df), 1955)    
    def test_sonde_ysi_exo2(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(len(df), 1775)    
    def test_sonde_ysi_exobackup(self):
        metadata, df = sonde3.sonde("tests/ysi_test_files/spotchecks-galveston-180618-081639.csv")
        self.assertEqual(len(df), 32)    
    def test_sonde_lowell(self):
        metadata, df = sonde3.sonde("tests/lowell_test_files/1603103_SAB_05122016.csv")
        self.assertEqual(len(df), 3026)  
               

class TestSonde_sonde_filepointer(unittest.TestCase):
   
    
    def test_sonde_ysi_binary(self):
        fid = open("tests/ysi_test_files/SA08.dat", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 700)
        fid.close
    def test_sonde_ysi_cdf(self):
        fid = open("tests/ysi_test_files/SA08.CDF", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 700)
        fid.close
    def test_sonde_ysi_ascii(self):
        fid = open("tests/ysi_test_files/0917GEB.txt", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 1760) 
        fid.close
    def test_sonde_ysi_exo(self):
        fid = open("tests/ysi_test_files/GE-SA-B_17H104157_090617_060000.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 1955)  
        fid.close
    def test_sonde_ysi_exo2(self):
        fid = open("tests/ysi_test_files/EMBData_Retrieved10.3.2019.csv", 'rb')
        metadata, df = sonde3.sonde("tests/ysi_test_files/EMBData_Retrieved10.3.2019.csv")
        self.assertEqual(len(df), 1775)
        fid.close()
    def test_sonde_ysi_exobackup(self):
        fid = open("tests/ysi_test_files/spotchecks-galveston-180618-081639.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 32)    
        fid.close()
    def test_sonde_lowell(self):
        fid = open("tests/lowell_test_files/1603103_SAB_05122016.csv", 'rb')
        metadata, df = sonde3.sonde(fid)
        self.assertEqual(len(df), 3026)  
        fid.close()
      
    
class TestSonde_dependencies(unittest.TestCase):
    def test_pandas_version(self):
        self.assertEqual(pandas.__version__, "0.25.3")
    def test_python(self):
        self.assertEqual(sys.version[:5], "3.6.8")

                                
            
if __name__ == '__main__':
    unittest.main()