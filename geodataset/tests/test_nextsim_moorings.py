from unittest import TestCase, mock

from geodataset.nextsim_moorings import Moorings
from geodataset.utils import BadAreaDefinition


class MooringsTestCases(TestCase):

    def test_moorings_instantiation_with_another_pattern_of_filename(self):
        """
        Mooring class belongs to the files that starts with "Moorings". Other files should bring the
        'BadAreaDefinition' exception.
        """
        with self.assertRaises(BadAreaDefinition):
            Moorings("")


    @mock.patch("nextsim_moorings.MooringsAreaDefinition.__init__", side_effect=IndexError)
    def test_moorings_instantiation_without_area_definition_class(self, mock_init):
        """
        In the case of lack of area definition for moorings files, IndexError is raised which must be
        raised as a customized 'BadAreaDefinition' error.
        """
        with self.assertRaises(BadAreaDefinition):
            Moorings("Moorings_1234.nc")#"Moorings_1234.nc"is not a existing file!

    def test_moorings_class_with_a_healthy_file_loading(self):
        """
        A healthy moorings file should be loaded properly with correct type.
        """
        test_geodataset = Moorings("geodataset/tests/data/Moorings_2021d179.nc")
        self.assertIsInstance(test_geodataset, Moorings)
