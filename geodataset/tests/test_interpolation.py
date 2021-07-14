import os
from os.path import join
from unittest import TestCase

from geodataset.geo_dataset import GeoDataset
from geodataset.interpolation import GridGridInterpolator
from geodataset.customized_geo_dataset import Moorings
from pyresample.bilinear import NumpyBilinearResampler


class InterpolationTestCases(TestCase):
    def test_resampling_between_two_files(self):
        """Test that the resampler is set correctly with all its builtin attributes"""
        target = GeoDataset(join(os.environ['TEST_DATA_DIR'], "ice_conc_nh_polstere-100_multi_200611151200.nc"))
        source = Moorings(join(os.environ['TEST_DATA_DIR'], "Moorings_2021d179.nc"))
        test_ggi = GridGridInterpolator(source.area, target.area, method=NumpyBilinearResampler,
                                        radius_of_influence=15000
                                       )
        self.assertEqual(test_ggi.resampler._source_geo_def, source.area)
        self.assertEqual(test_ggi.resampler._target_geo_def, target.area)
        self.assertEqual(test_ggi.resampler._radius_of_influence, 15000)
