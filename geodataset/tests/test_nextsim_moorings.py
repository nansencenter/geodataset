import os
from os.path import join
import unittest
from unittest import TestCase, mock

from geodataset.customized_geo_dataset import Moorings
from geodataset.utils import BadAreaDefinition

from geodataset.tests.base_test_class import GeodatasetTestBase

class MooringsTestCases(GeodatasetTestBase):

    def test_moorings_instantiation_with_another_pattern_of_filename(self):
        """
        Mooring class belongs to the files that starts with "Moorings". Other files should bring the
        'BadAreaDefinition' exception.
        """
        with self.assertRaises(BadAreaDefinition):
            Moorings("")

    @mock.patch("geodataset.area_definitions.MooringsAreaDefinition.__init__", return_value=None)
    def test_moorings_instantiation_without_area_definition_class(self, mock_init):
        """
        In the case of lack of addressed files, FileNotFoundError must be raised.
        """
        with self.assertRaises(FileNotFoundError):
            Moorings("Moorings_1234.nc") # "Moorings_1234.nc"is not a existing file!

    def test_moorings_class_with_a_healthy_file_loading(self):
        """
        A healthy moorings file should be loaded properly with correct type.
        """
        test_geodataset = Moorings(self.moorings_filename)
        self.assertIsInstance(test_geodataset, Moorings)

if __name__ == "__main__":
    unittest.main()