import os
from os.path import join
from unittest import TestCase

from geodataset.geo_dataset import GeoDataset
from geodataset.customized_geo_dataset import Moorings
from geodataset.tools import open_netcdf

from geodataset.tests.base_test_class import GeodatasetTestBase

class ToolsTestCases(GeodatasetTestBase):

    def test_method_open_netcdf_for_meaningless_file_address(self):
        """meaningless file_address should not result in BadAreaDefinition, instead it must raise
        the ValueError with customized message. BadAreaDefinition is only for controlled exceptions
        in order to switch from one candidate class to the next candidate for instantiation."""
        with self.assertRaises(ValueError) as error:
            open_netcdf("")
        self.assertEqual("Can not find proper geodataset-based class for this file: ",
                         str(error.exception)
                        )

    def test_method_open_netcdf_for_a_healthy_file(self):
        """a healthy file should be returned as a proper instance of formats after opening """
        test_obj = open_netcdf(self.osisaf_filename)
        self.assertTrue(isinstance(test_obj, GeoDataset))
        del test_obj
        test_obj = open_netcdf(self.moorings_filename)
        self.assertTrue(isinstance(test_obj, Moorings))
        del test_obj
