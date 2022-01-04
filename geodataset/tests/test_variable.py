import os
from os.path import join
import unittest
from unittest import TestCase

import numpy as np
from geodataset.variable import exchange_names, var_object
from netCDF4 import Dataset

from geodataset.tests.base_test_class import GeodatasetTestBase

class VariableTestCases(GeodatasetTestBase):
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

if __name__ == '__main__':
    unittest.main(failfast=True)
