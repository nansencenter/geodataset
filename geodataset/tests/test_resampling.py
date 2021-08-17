import os
import pickle
from os.path import join
from unittest import TestCase, mock

import numpy as np
from geodataset.interpolation import GridGridInterpolator
from geodataset.tools import open_netcdf
from pyresample.bilinear import NumpyBilinearResampler


class ResamplingTestCases(TestCase):

    def test_resampling_calculation_between_two_files(self):
        """Test that the resampling calculation is done and compare the result with
        the previously done which is stored in a pickled file"""
        target = open_netcdf(join(os.environ['TEST_DATA_DIR'], "ice_conc_nh_polstere-100_multi_200611151200.nc"))
        source = open_netcdf(join(os.environ['TEST_DATA_DIR'], "Moorings_2021d179.nc"))
        ggi = GridGridInterpolator(
                    source.area, target.area, method=NumpyBilinearResampler,
                    radius_of_influence=15000
                                  )
        concentration_from_nc_file = source.get_var('sea_ice_concentration', time_index=0).values
        resampled_data = ggi(concentration_from_nc_file)#newly calculated resampled data
        with open(join(os.environ['TEST_DATA_DIR'], "pickled.p"), 'rb') as pickle_file:
            resampled_data_from_pickled_file = pickle.load(pickle_file)
        #test that the newly calculated one is equal to the previousely calculated one
        np.testing.assert_equal(resampled_data, resampled_data_from_pickled_file)
