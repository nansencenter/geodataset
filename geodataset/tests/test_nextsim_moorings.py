import os
from os.path import join
from unittest import TestCase, mock

from geodataset.customized_geo_dataset import Moorings
from geodataset.utils import BadAreaDefinition


class MooringsTestCases(TestCase):

    def test_moorings_instantiation_with_another_pattern_of_filename(self):
        """
        Mooring class belongs to the files that starts with "Moorings". Other files should bring the
        'BadAreaDefinition' exception.
        """
        with self.assertRaises(BadAreaDefinition):
            Moorings("")

    @mock.patch("area_definitions.MooringsAreaDefinition.__init__", return_value=None)
    def test_moorings_instantiation_without_area_definition_class(self, mock_init):
        """
        In the case of lack of addressed files, FileNotFoundError must be raised.
        """
        with self.assertRaises(FileNotFoundError):
            Moorings("Moorings_1234.nc")#"Moorings_1234.nc"is not a existing file!

    def test_moorings_class_with_a_healthy_file_loading(self):
        """
        A healthy moorings file should be loaded properly with correct type.
        """
        test_geodataset = Moorings(join(os.environ['TEST_DATA_DIR'], "Moorings_2021d179.nc"))
        self.assertIsInstance(test_geodataset, Moorings)
