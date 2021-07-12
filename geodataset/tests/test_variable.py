from unittest import TestCase

import numpy as np
from geodataset.variable import exchange_names, var_object
from netCDF4 import Dataset


class VariableTestCases(TestCase):
    def test_method_exchange_name(self):
        """
        test that the names are correctly exchanged into the proper name inside the netcdf file
        """
        with Dataset("data/ice_conc_nh_polstere-100_multi_200611151200.nc") as nc:
            answer1 = exchange_names('sea_ice_concentration', nc.variables)
            answer2 = exchange_names('sic', nc.variables)
            answer3 = exchange_names('concentration', nc.variables)
            self.assertTrue(answer1 == answer2 == answer3 == 'ice_conc')

            with self.assertRaises(ValueError):
                exchange_names('blablabla', nc.variables)

    def test__var_object__class(self):
        """
        test that 'var_object' class is working properly. This includes the mask and the data within
        """
        arr = np.ma.masked_values([[1.0, 99], [3.0, 400.0]], 99)
        var = var_object(arr.data, arr.mask)
        self.assertEqual(var.shape, (2, 2))
        self.assertEqual(var.min(), 1.0)
        self.assertEqual(var.max(), 400.0)
        np.testing.assert_equal(var[:,:], np.ma.masked_values([[1.0, 99], [3.0, 400.0]], 99))
