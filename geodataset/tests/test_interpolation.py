import os
from unittest import TestCase

from geodataset.geo_dataset import GeoDataset
from geodataset.interpolation import GridGridInterpolator
from geodataset.customized_geo_dataset import Moorings
from pyresample.bilinear import NumpyBilinearResampler

from geodataset.tests.base_test_class import GeodatasetTestBase

class InterpolationTestCases(GeodatasetTestBase):
    def test_resampling_between_two_files(self):
        """Test that the resampler is set correctly with all its builtin attributes"""
        target = GeoDataset(self.osisaf_filename)
        source = Moorings(self.moorings_filename)
        test_ggi = GridGridInterpolator(source.area, target.area, method=NumpyBilinearResampler,
                                        radius_of_influence=15000
                                       )
        self.assertEqual(test_ggi.resampler._source_geo_def, source.area)
        self.assertEqual(test_ggi.resampler._target_geo_def, target.area)
        self.assertEqual(test_ggi.resampler._radius_of_influence, 15000)
