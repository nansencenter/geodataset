from unittest import TestCase, mock

import netcdftime
from netCDF4 import Dataset
from utils import get_time_converter, get_time_name


class UtilsTestCases(TestCase):

    def test_get_time_name(self):
        """ Test that the name of variable that contains time inside the netcdf file is correctly
        found by the method."""
        with Dataset("data/ice_conc_nh_polstere-100_multi_200611151200.nc") as nc:
            answer = get_time_name(nc)
            self.assertEqual(answer, 'time')

    def test_get_time_converter(self):
        ""
        possible_units = [
            'days since 1900-1-1 0:0:0 +0',
            'seconds since 2000-01-01 00:00:00',
            'hours since 19500101 000000',
        ]
        time = mock.MagicMock()
        for time.units in possible_units:
            tc = get_time_converter(time)
            self.assertIsInstance(tc, netcdftime._netcdftime.utime)
        self.assertEqual(tc.origin, netcdftime._netcdftime.datetime(1950, 1, 1, 0, 0, 0, 0, -1, 1))
        self.assertEqual(tc.unit_string, 'hours since 1950-01-01 00-00-00')
        self.assertEqual(tc.units, 'hours')
        time.units = 'bla bla bla bla'
        with self.assertRaises(ValueError):
            tc = get_time_converter(time)
