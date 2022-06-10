import datetime as dt
import glob
from mock import patch, call, Mock, MagicMock, DEFAULT
import os
import subprocess
import unittest

from netCDF4 import Dataset
import numpy as np
import pyproj
from pyproj.exceptions import CRSError

from geodataset.custom_geodataset import UniBremenMERISAlbedoMPFBase

from geodataset.utils import InvalidDatasetError
from geodataset.tests.base_for_tests import BaseForTests


class UniBremenMERISAlbedoMPFBaseTest(BaseForTests):

    def test_get_xy_arrays_1(self):
        """ test get_xy_arrays with default options """
        x, y = UniBremenMERISAlbedoMPFBase.get_xy_arrays()
        dx = x[0,1] - x[0,0]
        dy = y[1,0] - y[0,0]
        self.assertEqual(dx, 12500.)
        self.assertEqual(dy, 12500.)
        self.assertEqual(x[0,0] - .5 * dx, -3850.e3)
        self.assertEqual(y[0,0] - .5 * dy, -5350.e3)
        self.assertEqual(x.shape, (896,608))
        self.assertEqual(y.shape, (896,608))

    def test_get_xy_arrays_2(self):
        """ test get_xy_arrays with ij_range passed """
        x0, y0 = UniBremenMERISAlbedoMPFBase.get_xy_arrays()
        x, y = UniBremenMERISAlbedoMPFBase.get_xy_arrays(ij_range=[3,10,6,21])
        self.assertTrue(np.allclose(x0[3:11,6:22], x))
        self.assertTrue(np.allclose(y0[3:11,6:22], y))

    @patch.multiple(UniBremenMERISAlbedoMPFBase,
            __init__=MagicMock(return_value=None),
            get_xy_arrays=MagicMock(return_value=('x', 'y')),
            projection=MagicMock(return_value=('lon', 'lat')),
            )
    def test_get_lonlat_arrays(self):
        obj = UniBremenMERISAlbedoMPFBase()

        lon, lat = obj.get_lonlat_arrays(a=1, b=2)
        self.assertEqual(lon, 'lon')
        self.assertEqual(lat, 'lat')
        obj.get_xy_arrays.assert_called_once_with(a=1, b=2)
        obj.projection.assert_called_once_with('x', 'y', inverse=True)

    @patch.multiple(UniBremenMERISAlbedoMPFBase,
            __init__=MagicMock(return_value=None),
            filepath=DEFAULT,
            )
    def test_datetimes_1(self, **kwargs):
        """ test for older filename """
        dto = dt.datetime(2017,5,1)
        kwargs['filepath'].return_value = dto.strftime('a/b/mpd_%Y%m%d.nc')
        obj = UniBremenMERISAlbedoMPFBase()
        self.assertEqual(obj.datetimes, [dto])


    @patch.multiple(UniBremenMERISAlbedoMPFBase,
            __init__=MagicMock(return_value=None),
            filepath=DEFAULT,
            )
    def test_datetimes_2(self, **kwargs):
        """ test for newer filename """
        dto = dt.datetime(2021,5,1)
        kwargs['filepath'].return_value = dto.strftime('a/b/mpd_%Y%m%d_NR.nc')
        obj = UniBremenMERISAlbedoMPFBase()
        self.assertEqual(obj.datetimes, [dto])


if __name__ == "__main__":
    unittest.main()
