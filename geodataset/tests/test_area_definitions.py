import os
from os.path import join
from unittest import TestCase, mock

from area_definitions import CustomAreaDefinitionBase, MooringsAreaDefinition
from geodataset.utils import BadAreaDefinition


class CustomAreaDefinitionTestCases(TestCase):

    @mock.patch("area_definitions.CustomAreaDefinitionBase._set_corner_coordinates")
    @mock.patch("area_definitions.CustomAreaDefinitionBase._set_shape")
    @mock.patch("area_definitions.CustomAreaDefinitionBase._set_extent")
    @mock.patch("area_definitions.CustomAreaDefinitionBase._set_area_id")
    @mock.patch("area_definitions.CustomAreaDefinitionBase.__init__", return_value=None)
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


class ValueBasedAreaDefinitionTestCases(TestCase):
    """if the generic computational methods can calculated the number for one example, they can do
    the same for every type of file. Here in this case mooring file is selected as an example file"""
    def setUp(self):
        self.testing_areadefinition = MooringsAreaDefinition(join(os.environ['TEST_DATA_DIR'], "Moorings_2021d179.nc"))

    def tearDown(self):
        del self.testing_areadefinition

    def test_method__set_corner_coordinates(self):
        """test that the coordinates of corners are correctly set"""
        self.testing_areadefinition._set_corner_coordinates()
        self.assertEqual(self.testing_areadefinition.x_ur, 3547679.7638763348)
        self.assertEqual(self.testing_areadefinition.x_ll, -3365213.0718218326)
        self.assertEqual(self.testing_areadefinition.y_ur, -4016593.7395200725)
        self.assertEqual(self.testing_areadefinition.y_ll, 2615518.679565192)

    def test_method__set_shape(self):
        """test that the shape is correctly set"""
        self.testing_areadefinition._set_shape()
        self.assertEqual(self.testing_areadefinition.shape, (2367, 2467))

    def test_method__set_area_id(self):
        """test that the area_id is correctly set"""
        self.testing_areadefinition._set_area_id()
        self.assertEqual(self.testing_areadefinition.area_id, 'id for MooringsAreaDefinition object')


class ValueBasedMooringsAreaDefinitionTestCases(TestCase):
    def test_method_area_extent(self):
        """Test that the corners and the area extent of AreaDefinition is set correctly"""
        self.testing_areadefinition = MooringsAreaDefinition(join(os.environ['TEST_DATA_DIR'], "Moorings_2021d179.nc"))
        self.testing_areadefinition._set_corner_coordinates()
        self.testing_areadefinition._set_extent()
        self.assertEqual(self.testing_areadefinition.width, 6912978.442985907)
        self.assertEqual(self.testing_areadefinition.height, 6632203.801141923)
        self.assertEqual(self.testing_areadefinition.cell_size_x, 2803.316481340595)
        self.assertEqual(self.testing_areadefinition.cell_size_y, 2803.1292481580404)
        self.assertEqual(self.testing_areadefinition.x_corner_ll, -3366614.730062503)
        self.assertEqual(self.testing_areadefinition.x_corner_ur, 3549081.422117005)
        self.assertEqual(self.testing_areadefinition.y_corner_ll, 2614117.114941113)
        self.assertEqual(self.testing_areadefinition.y_corner_ur, -4015192.1748959934)
        self.assertEqual(self.testing_areadefinition.area_extent,
                   (-3366614.730062503, 2614117.114941113, 3549081.422117005, -4015192.1748959934)
                        )
        del self.testing_areadefinition
