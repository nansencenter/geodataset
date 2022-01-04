import os
from os.path import join
import unittest
from unittest import TestCase, mock

from geodataset.area_definitions import CustomAreaDefinitionBase, MooringsAreaDefinition
from geodataset.utils import BadAreaDefinition

from geodataset.tests.base_test_class import GeodatasetTestBase

class CustomAreaDefinitionTestCases(GeodatasetTestBase):

    @mock.patch("geodataset.area_definitions.CustomAreaDefinitionBase._set_corner_coordinates")
    @mock.patch("geodataset.area_definitions.CustomAreaDefinitionBase._set_shape")
    @mock.patch("geodataset.area_definitions.CustomAreaDefinitionBase._set_extent")
    @mock.patch("geodataset.area_definitions.CustomAreaDefinitionBase._set_area_id")
    @mock.patch("geodataset.area_definitions.CustomAreaDefinitionBase.__init__", return_value=None)
    def test_method_create_area(self, mock_init, mock_set_area_id, mock_set_extent,
                                  mock_set_shape, mock_set_corner_coordinates
                               ):
        """ Test that create area method calls other methods properly """
        custom_areadefinition = CustomAreaDefinitionBase("")
        custom_areadefinition._create_area()
        mock_set_corner_coordinates.assert_called()
        mock_set_shape.assert_called()
        mock_set_extent.assert_called()
        mock_set_area_id.assert_called()


class ValueBasedAreaDefinitionTestCases(GeodatasetTestBase):
    """if the generic computational methods can calculated the number for one example, they can do
    the same for every type of file. Here in this case mooring file is selected as an example file"""
    def setUp(self):
        super().setUp()
        self.testing_areadefinition = MooringsAreaDefinition(self.moorings_filename)

    def tearDown(self):
        del self.testing_areadefinition

    def test_method__set_corner_coordinates(self):
        """test that the coordinates of corners are correctly set"""
        self.testing_areadefinition._set_corner_coordinates()
        self.assertAlmostEqual(self.testing_areadefinition.x_ur, 1643649.8459712546)
        self.assertAlmostEqual(self.testing_areadefinition.x_ll, -2256350.2237977847)
        self.assertAlmostEqual(self.testing_areadefinition.y_ur, -1232777.8752833942)
        self.assertAlmostEqual(self.testing_areadefinition.y_ll, 2017222.0174571355)

    def test_method__set_shape(self):
        """test that the shape is correctly set"""
        self.testing_areadefinition._set_shape()
        self.assertAlmostEqual(self.testing_areadefinition.shape, (326, 391))

    def test_method__set_area_id(self):
        """test that the area_id is correctly set"""
        self.testing_areadefinition._set_area_id()
        self.assertAlmostEqual(self.testing_areadefinition.area_id, 'id for MooringsAreaDefinition object')


class ValueBasedMooringsAreaDefinitionTestCases(GeodatasetTestBase):
    def test_method_area_extent(self):
        """Test that the corners and the area extent of AreaDefinition is set correctly"""
        self.testing_areadefinition = MooringsAreaDefinition(self.moorings_filename)
        self.testing_areadefinition._set_corner_coordinates()
        self.testing_areadefinition._set_extent()
        self.assertAlmostEqual(self.testing_areadefinition.width, 3899999.349279247, 1)
        self.assertAlmostEqual(self.testing_areadefinition.height, 3249999.7459878484, 1)
        self.assertAlmostEqual(self.testing_areadefinition.cell_size_x, 9999.998331485249, 1)
        self.assertAlmostEqual(self.testing_areadefinition.cell_size_y, 9999.99921842415, 1)
        self.assertAlmostEqual(self.testing_areadefinition.x_corner_ll, -2261350.2229635273, 1)
        self.assertAlmostEqual(self.testing_areadefinition.x_corner_ur, 1648649.8451369973, 1)
        self.assertAlmostEqual(self.testing_areadefinition.y_corner_ll, 2012222.0178479233, 1)
        self.assertAlmostEqual(self.testing_areadefinition.y_corner_ur, -1227777.875674182, 1)
        self.assertAlmostEqual(self.testing_areadefinition.area_extent,
            (-2261350.2229635273, 2012222.0178479233, 1648649.8451369973, -1227777.875674182), 1)
        del self.testing_areadefinition


if __name__ == "__main__":
    unittest.main(failfast=True)
