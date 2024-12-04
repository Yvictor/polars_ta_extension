#!/usr/bin/python
"""
Test of Python wrapper to ta_func
""" 

import sys
import unittest
sys.path.insert(0,'../../../lib/python')

from TaLib import *



class ta_func_test(unittest.TestCase):

    # series from "daily" data of TA_SIMULATOR
    series = [ 91.500, 94.815, 94.375, 95.095, 93.780, 94.625, 92.530, 92.750, 90.315, 92.470, 96.125, 97.250, 98.500, 89.875, 91.000, 92.815, 89.155, 89.345, 91.625, 89.875, 88.375, 87.625, 84.780, 83.000, 83.500, 81.375, 84.440, 89.250, 86.375, 86.250, 85.250, 87.125, 85.815, 88.970, 88.470, 86.875, 86.815, 84.875, 84.190, 83.875, 83.375, 85.500, 89.190, 89.440, 91.095, 90.750, 91.440, 89.000, 91.000, 90.500, 89.030, 88.815, 84.280, 83.500, 82.690, 84.750, 85.655, 86.190, 88.940, 89.280, 88.625, 88.500, 91.970, 91.500, 93.250, 93.500, 93.155, 91.720, 90.000, 89.690, 88.875, 85.190, 83.375, 84.875, 85.940, 97.250, 99.875, 104.940, 106.000, 102.500, 102.405, 104.595, 106.125, 106.000, 106.065, 104.625, 108.625, 109.315, 110.500, 112.750, 123.000, 119.625, 118.750, 119.250, 117.940, 116.440, 115.190, 111.875, 110.595, 118.125, 116.000, 116.000, 112.000, 113.750, 112.940, 116.000, 120.500, 116.620, 117.000, 115.250, 114.310, 115.500, 115.870, 120.690, 120.190, 120.750, 124.750, 123.370, 122.940, 122.560, 123.120, 122.560, 124.620, 129.250, 131.000, 132.250, 131.000, 132.810, 134.000, 137.380, 137.810, 137.880, 137.250, 136.310, 136.250, 134.630, 128.250, 129.000, 123.870, 124.810, 123.000, 126.250, 128.380, 125.370, 125.690, 122.250, 119.370, 118.500, 123.190, 123.500, 122.190, 119.310, 123.310, 121.120, 123.370, 127.370, 128.500, 123.870, 122.940, 121.750, 124.440, 122.000, 122.370, 122.940, 124.000, 123.190, 124.560, 127.250, 125.870, 128.860, 132.000, 130.750, 134.750, 135.000, 132.380, 133.310, 131.940, 130.000, 125.370, 130.130, 127.120, 125.190, 122.000, 125.000, 123.000, 123.500, 120.060, 121.000, 117.750, 119.870, 122.000, 119.190, 116.370, 113.500, 114.250, 110.000, 105.060, 107.000, 107.870, 107.000, 107.120, 107.000, 91.000, 93.940, 93.870, 95.500, 93.000, 94.940, 98.250, 96.750, 94.810, 94.370, 91.560, 90.250, 93.940, 93.620, 97.000, 95.000, 95.870, 94.060, 94.620, 93.750, 98.000, 103.940, 107.870, 106.060, 104.500, 105.000, 104.190, 103.060, 103.420, 105.270, 111.870, 116.000, 116.620, 118.280, 113.370, 109.000, 109.700, 109.250, 107.000, 109.190, 110.000, 109.200, 110.120, 108.000, 108.620, 109.750, 109.810, 109.000, 108.750, 107.870 ]


    def test_TA_MAX(self):
        retCode, begIdx, result = TA_MAX( 0, len(ta_func_test.series)-1, ta_func_test.series, 4 )
        self.assertEqual( retCode, TA_SUCCESS )
        self.assertEqual( begIdx, TA_MAX_Lookback(4) )
        self.assert_( result )
        self.assertEqual( len(ta_func_test.series) - len(result), begIdx )
        self.assertEqual( result[2], 95.095 )
        self.assertEqual( result[3], 95.095 )
        self.assertEqual( result[4], 94.625 )
        self.assertEqual( result[5], 94.625 )
        

    def test_TA_MIN(self):
        retCode, begIdx, result = TA_MIN( 0, len(ta_func_test.series)-1, ta_func_test.series, 4 )
        self.assertEqual( retCode, TA_SUCCESS )
        self.assertEqual( begIdx, TA_MIN_Lookback(4) )
        self.assert_( result )
        self.assertEqual( len(ta_func_test.series) - len(result), begIdx )
        self.assertEqual( result[1], 93.780 )
        self.assertEqual( result[2], 93.780 )
        self.assertEqual( result[3], 92.530 )
        self.assertEqual( result[4], 92.530 )
        

    def test_TA_BBANDS(self):
        retCode, begIdx, result1, result2, result3 = TA_BBANDS(
                0, len(ta_func_test.series)-1, ta_func_test.series, 20, 2.0, 2.0, TA_MAType_EMA)
        self.assertEqual( retCode, TA_SUCCESS )
        self.assertEqual( begIdx, TA_BBANDS_Lookback(20, 2.0, 2.0, TA_MAType_EMA) )
        self.assert_( result1 )
        self.assert_( result2 )
        self.assert_( result3 )
        self.assertEqual( len(ta_func_test.series) - len(result1), begIdx )
        self.assertEqual( len(ta_func_test.series) - len(result2), begIdx )
        self.assertEqual( len(ta_func_test.series) - len(result3), begIdx )
        self.assert_( abs(result1[0] - 98.0734) < 1e-3 )
        self.assert_( abs(result2[0] - 92.8910) < 1e-3 )
        self.assert_( abs(result3[0] - 87.7086) < 1e-3 )
        self.assert_( abs(result1[13] - 93.674) < 1e-3 )
        self.assert_( abs(result2[13] - 87.679) < 1e-3 )
        self.assert_( abs(result3[13] - 81.685) < 1e-3 )


    def test_TA_DEMA(self):
        retCode, begIdx, result = TA_DEMA(0, len(ta_func_test.series)-1, ta_func_test.series ) # default optInTimePeriod
        self.assertEqual( retCode, TA_SUCCESS )
        self.assertEqual( begIdx, TA_DEMA_Lookback(30) )
        self.assert_( result )
        self.assertEqual( len(ta_func_test.series) - len(result), begIdx )
        self.assert_( abs(result[1] - 86.765) < 1e-3 )
        self.assert_( abs(result[2] - 86.942) < 1e-3 )
        self.assert_( abs(result[3] - 87.089) < 1e-3 )
        self.assert_( abs(result[4] - 87.656) < 1e-3 )



if __name__ == '__main__':
    print "TA-Lib ", TA_GetVersionString()
    print "Testing ta_func...";
    unittest.main()
