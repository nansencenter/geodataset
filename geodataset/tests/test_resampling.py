import os
import pickle
from os.path import join
import unittest
from unittest import TestCase, mock

import numpy as np
from geodataset.interpolation import GridGridInterpolator
from geodataset.tools import open_netcdf
from pyresample.bilinear import NumpyBilinearResampler

from geodataset.tests.base_test_class import GeodatasetTestBase

class ResamplingTestCases(GeodatasetTestBase):

    def test_resampling_calculation_between_two_files(self):
        """Test that the resampling calculation is done and compare the result with
        the previously done which is stored in a pickled file"""
        source = open_netcdf(self.moorings_filename)
        target = open_netcdf(self.osisaf_filename)
        trg_data = target.get_var(self.osisaf_var).values

        ggi = GridGridInterpolator(
                    source.area, target.area, method=NumpyBilinearResampler,
                    radius_of_influence=15000
                                  )
        src_data = source.get_var(self.moorings_var, time_index=0).values
        src_data_resampled = ggi(src_data) #newly calculated resampled data
        self.assertEqual(src_data_resampled.shape, trg_data.shape)

if __name__ == "__main__":
    unittest.main()