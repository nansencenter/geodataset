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

from geodataset.custom_geodataset import UniBremenAlbedoMPF

from geodataset.utils import InvalidDatasetError
from geodataset.tests.base_for_tests import BaseForTests


class UniBremenAlbedoMPFBaseTest(BaseForTests):

    def test_get_xy_arrays_1(self):
        """ test get_xy_arrays with default options """
        x, y = UniBremenAlbedoMPF.get_xy_arrays()
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
        x0, y0 = UniBremenAlbedoMPF.get_xy_arrays()
        x, y = UniBremenAlbedoMPF.get_xy_arrays(ij_range=[3,10,6,21])
        self.assertTrue(np.allclose(x0[3:10,6:21], x))
        self.assertTrue(np.allclose(y0[3:10,6:21], y))

    @patch.multiple(UniBremenAlbedoMPF,
            __init__=MagicMock(return_value=None),
            get_xy_arrays=MagicMock(return_value=('x', 'y')),
            projection=MagicMock(return_value=('lon', 'lat')),
            )
    def test_get_lonlat_arrays(self):
        obj = UniBremenAlbedoMPF()

        lon, lat = obj.get_lonlat_arrays(a=1, b=2)
        self.assertEqual(lon, 'lon')
        self.assertEqual(lat, 'lat')
        obj.get_xy_arrays.assert_called_once_with(a=1, b=2)
        obj.projection.assert_called_once_with('x', 'y', inverse=True)

    @patch.multiple(UniBremenAlbedoMPF,
            __init__=MagicMock(return_value=None),
            filepath=DEFAULT,
            )
    def test_datetimes(self, **kwargs):
        dto = dt.datetime(2023,5,1,12)
        kwargs['filepath'].return_value = dto.strftime('a/b/mpd_%Y%m%d.nc')
        obj = UniBremenAlbedoMPF()
        self.assertEqual(obj.datetimes, [dto])


class NERSCProductBaseTest(BaseForTests):

    @property
    def x(self):
        return np.linspace(0.,1.,6)

    @property
    def y(self):
        return np.linspace(1.,2.,8)

    @patch.multiple(NERSCProductBase,
            __init__=MagicMock(return_value=None),
            __getitem__=DEFAULT,
            projection=DEFAULT,
            )
    def test_get_lonlat_arrays(self, __getitem__, projection):
        """ test for older filename """
        def mock_getitem(key):
            if key == "x":
                return self.x
            return self.y

        obj = NERSCProductBase()
        __getitem__.side_effect = mock_getitem
        projection.return_value = ('lon', 'lat')

        i0 = 2
        i1 = 5
        j0 = 1
        j1 = 6
        x0, y0 = np.meshgrid(self.x[j0:j1], self.y[i0:i1])

        lon, lat = obj.get_lonlat_arrays(ij_range=(i0, i1, j0, j1))
        self.assertEqual(lon, 'lon')
        self.assertEqual(lat, 'lat')
        self.assertEqual(__getitem__.mock_calls, [call('x'), call('y')])
        x, y = projection.mock_calls[0][1]
        self.assertTrue(np.allclose(x, x0))
        self.assertTrue(np.allclose(y, y0))
        self.assertEqual(projection.mock_calls[0][2], dict(inverse=True))


if __name__ == "__main__":
    unittest.main()
