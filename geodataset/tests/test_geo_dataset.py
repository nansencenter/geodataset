import os
from datetime import datetime
from os.path import join
import unittest
from unittest import TestCase, mock

import numpy as np
from geodataset.geo_dataset import GeoDataset, load_cf_area
from geodataset.utils import BadAreaDefinition

from geodataset.tests.base_test_class import GeodatasetTestBase

class GeodatasetTestCases(GeodatasetTestBase):

    def setUp(self):
        super().setUp()
        self.test_geodataset = GeoDataset(self.osisaf_filename)

    @mock.patch.object(GeoDataset, "_set_time_info")
    @mock.patch("geodataset.geo_dataset.load_cf_area", return_value=["return_value_for_load_cf_area", ''])
    def test_geodataset_instantiation(self,  mock_load_cf_area, mock_set_time):
        """
        'load_cf_area' function of pyresample must be used for setting the 'area' attribute of
        goedataset.
        """
        empty_geodataset = GeoDataset("")
        self.assertEqual(empty_geodataset.area, "return_value_for_load_cf_area")

    @mock.patch("geodataset.geo_dataset.load_cf_area", side_effect=ValueError)
    def test_geodataset_unacceptable_instantiation_by_pyresample(self,  mock_load_cf_area):
        """
        If pyresample can't read the netcdf file, then the ValueError is raised afterwards. This
        must be raised in terms of our customized exception 'BadAreaDefinition', not with
        ValueError itself.
        """
        with self.assertRaises(BadAreaDefinition):
            empty_geodataset = GeoDataset("")

    def test_method_get_var(self):
        """Test the 'get_var' method ability to bring the variable properly"""
        variable = self.test_geodataset.get_var(self.osisaf_var)
        self.assertEqual(variable.shape, (177, 119))
        self.assertEqual(variable.units, self.osisaf_units)
        self.assertEqual(variable.standard_name, self.osisaf_std_name)
        self.assertEqual(variable.dimensions, ('yc', 'xc'))
        self.assertAlmostEqual(variable.max(), self.osisaf_max, 5)

    def test_method_set_time_info(self):
        """Test the ability of setting the datetimes and other time related attributes correctly"""
        self.assertEqual(self.test_geodataset.number_of_time_records, 1)
        self.assertEqual(self.test_geodataset.time_name, 'time')
        self.assertEqual(self.test_geodataset.timeunits, 'hour')
        self.assertEqual(self.test_geodataset.time_dim, True)
        self.assertEqual(self.test_geodataset.datetimes, [datetime(2022, 1, 3, 12, 0)])

    def test_method_nearestDate(self):
        """Test the ability of finding the nearest date to a specific date. 2007 is near to 2006 (in
        netcdf file) than the 2010."""
        self.test_geodataset.datetimes.append(datetime(2000, 1, 1, 12, 0))
        ans, ans_index = self.test_geodataset.nearestDate(datetime(2020, 1, 1, 12, 0))
        self.assertEqual(ans, datetime(2022, 1, 3, 12, 0))
        self.assertEqual(ans_index, 0)

if __name__ == "__main__":
    unittest.main()