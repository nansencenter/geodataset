import os
import numpy as np
import unittest
import datetime as dt
from mock import patch, call, MagicMock, DEFAULT
import subprocess

from geodataset.tests.geodataset_test_base import GeodatasetTestBase
from geodataset.geodataset import GeoDataset, Dataset, ProjectionInfo

class GeoDatasetTest(GeodatasetTestBase):
    def test_init(self):
        f = os.path.join(self.test_data_dir, 'ice_drift_nh_polstere-625_multi-oi_202201011200-202201031200.nc')
        ds = Dataset(f, 'r')
        nc = GeoDataset(f, 'r')
        self.assertEqual(ds.ncattrs(), nc.ncattrs())
        self.assertEqual(list(ds.dimensions), list(nc.dimensions))
        self.assertEqual(list(ds.variables), list(nc.variables))
        self.assertEqual(vars(nc.projection), vars(ProjectionInfo()))
        self.assertEqual(nc.projection_names, ('Polar_Stereographic_Grid', 'polar_stereographic'))
        self.assertEqual(nc.spatial_dim_names, ('x', 'y'))
        self.assertEqual(nc.lonlat_names, ('longitude', 'latitude'))
        self.assertEqual(nc.time_name, 'time')
        self.assertFalse(nc.is_lonlat_dim)

    @patch.multiple(GeoDataset, __init__=MagicMock(return_value=None), dimensions=DEFAULT)
    def test_is_lonlat_dim(self, **kwargs):
        nc = GeoDataset()
        nc.lonlat_names = ('lon', 'lat')
        nc.dimensions = ('x', 'y')
        self.assertFalse(nc.is_lonlat_dim)
        nc.dimensions = ('lon', 'lat')
        self.assertTrue(nc.is_lonlat_dim)

    @patch.multiple(GeoDataset, __init__=MagicMock(return_value=None), convert_time_data=DEFAULT, variables=DEFAULT)
    def test_datetimes(self, **kwargs):
        nc = GeoDataset()
        nc.time_name = 'time_name'
        tdata = np.random.uniform(size=(3,))
        nc.variables = dict(time_name=tdata)
        kwargs['convert_time_data'].side_effect = lambda x:2*x

        dtimes = nc.datetimes
        self.assert_lists_equal(list(2*tdata), dtimes)
        self.assert_mock_has_calls(kwargs['convert_time_data'], [call(tdata)])

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None), createVariable=DEFAULT)
    def test_set_projection_variable(self, **kwargs):
        nc = GeoDataset()
        nc.projection_names = ('gm', 'gmn')
        nc.projection = MagicMock()
        nc.projection.ncattrs = MagicMock(return_value='ncatts')
        nc.set_projection_variable()

        nc.projection.ncattrs.assert_called_once_with('gmn')
        req_calls = [call('gm', 'i1'), call().setncatts('ncatts'),
                call().setncatts({'proj4': '+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-45 +x_0=0 +y_0=0 +R=6378273 +ellps=sphere +units=m +no_defs'})]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDataset, __init__=MagicMock(return_value=None), variables=DEFAULT,
            is_lonlat_dim=DEFAULT)
    def test_get_xy_dims_from_lonlat_1(self, **kwargs):
        lon = np.random.normal(size=(2,2))
        lat = np.random.normal(size=(2,2))
        nc = GeoDataset()
        nc.is_lonlat_dim = False
        nc.projection = MagicMock()
        nc.projection.pyproj = MagicMock(return_value = (2*lon, 3*lat))
        acc = 1e-2
        x = np.round(2*lon/acc)*acc
        y = np.round(3*lat/acc)*acc

        x2, y2 = nc.get_xy_dims_from_lonlat(lon, lat, accuracy=acc)
        self.assert_arrays_equal(x2, x)
        self.assert_arrays_equal(y2, y)
        self.assert_mock_has_calls(nc.projection.pyproj,
                [call(lon[0,:], lat[0,:]), call(lon[:,0], lat[:,0])])

    @patch.multiple(GeoDataset, __init__=MagicMock(return_value=None), variables=DEFAULT)
    @patch('geodataset.geodataset.vars')
    def test_convert_time_data(self, mock_vars, **kwargs):
        shp = (4,2)
        tdata = 1333195200*np.ones(shp)
        dto = dt.datetime(2020, 3, 31, 12)
        nc = GeoDataset()
        nc.time_name = 'time_name'
        mock_vars.return_value = dict(units='seconds since 1978-01-01 00:00:00', calendar='standard')
        nc.variables = dict(time_name='ncvar')

        dtimes = nc.convert_time_data(tdata)
        mock_vars.assert_called_with('ncvar')
        self.assertEqual(shp, dtimes.shape)
        self.assertTrue(np.all(dtimes==dto))
        self.assertIsInstance(dtimes, np.ndarray)

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None),
            createDimension=DEFAULT,
            createVariable=DEFAULT,
            )
    def test_set_xy_dims(self, **kwargs):
        nx = 2
        ny = 3
        x = np.random.normal(size=(nx,))
        y = np.random.normal(size=(ny,))

        nc = GeoDataset()
        nc.set_xy_dims(x, y)
        self.assert_mock_has_calls(kwargs['createDimension'],
                [call('y', ny), call('x', nx)])
        req_calls = [
                call('y', 'f8', ('y',), zlib=True),
                call().setncattr('standard_name', 'projection_y_coordinate'),
                call().setncattr('units', 'm'),
                call().setncattr('axis', 'Y'),
                call().__setitem__(slice(None, None, None), y),
                call('x', 'f8', ('x',), zlib=True),
                call().setncattr('standard_name', 'projection_x_coordinate'),
                call().setncattr('units', 'm'),
                call().setncattr('axis', 'X'),
                call().__setitem__(slice(None, None, None), x),
                ]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    def test_set_lonlat(self, **kwargs):

        slon = (2,2)
        slat = (3,3)
        lon = np.random.normal(size=slon)
        lat = np.random.normal(size=slat)

        nc = GeoDataset()
        nc.spatial_dim_names = ['x', 'y']
        nc.set_lonlat(lon, lat)
        req_calls = [
                call('longitude', 'f8', ('y', 'x'), zlib=True),
                call().setncattr('standard_name', 'longitude'),
                call().setncattr('long_name', 'longitude'),
                call().setncattr('units', 'degrees_east'),
                call().__setitem__(slice(None, None, None), lon),
                call('latitude', 'f8', ('y', 'x'), zlib=True),
                call().setncattr('standard_name', 'latitude'),
                call().setncattr('long_name', 'latitude'),
                call().setncattr('units', 'degrees_north'),
                call().__setitem__(slice(None, None, None), lat),
                ]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None),
            createDimension=DEFAULT,
            createVariable=DEFAULT,
            )
    def test_set_time_variables_dimensions(self, **kwargs):
        nc = GeoDataset()
        nt = 3
        time_inds = [1,2]
        time = np.random.normal(size=(nt,))
        time_bnds = np.random.normal(size=(nt,2))
        time_atts = dict(a1='A1', a2='A2', units='units')

        nc.set_time_variables_dimensions(time, time_atts, time_bnds)
        self.assert_mock_has_calls(kwargs['createDimension'], [call('time', None), call('nv', 2)])
        req_calls = [
                call('time', 'f8', ('time',), zlib=True), call().setncatts({'a1': 'A1', 'a2': 'A2', 'units': 'units', 'calendar': 'standard'}),
                call().__setitem__(slice(None, None, None), time),
                call('time_bnds', 'f8', ('time', 'nv'), zlib=True),
                call().setncattr('units', 'units'),
                call().__setitem__(slice(None, None, None), time_bnds),
                ]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    @patch('geodataset.geodataset.np.double')
    @patch('geodataset.geodataset.np.float32')
    def test_set_variable_1(self, f4, f8, **kwargs):
        ''' test f4 with _FillValue defined '''
        nc = GeoDataset()
        nc.projection_names = ('gm', 'gmn')
        nc.logger = MagicMock()
        atts = dict(a1='A1', a2='A2', _FillValue='fv')
        f4.return_value = 'fv4'
        nc.set_variable('vname', 'data', 'dims', atts, dtype='f4')
        f4.assert_called_once_with('fv')
        f8.assert_not_called()

        req_calls = [
                call('vname', 'f4', 'dims', fill_value='fv4', zlib=True),
                call().setncatts({'a1': 'A1', 'a2': 'A2', 'grid_mapping': 'gm'}),
                call().__setitem__(slice(None, None, None), 'data'),
                ]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDataset,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    @patch('geodataset.geodataset.np.double')
    @patch('geodataset.geodataset.np.float32')
    def test_set_variable_2(self, f4, f8, **kwargs):
        ''' test f8 with missing_value defined '''
        nc = GeoDataset()
        nc.projection_names = ('gm', 'gmn')
        nc.logger = MagicMock()
        atts = dict(a1='A1', a2='A2', missing_value='fv')
        f8.return_value = 'fv8'

        nc.set_variable('vname', 'data', 'dims', atts, dtype='f8')
        f8.assert_called_once_with('fv')
        f4.assert_not_called()
        req_calls = [
                call('vname', 'f8', 'dims', zlib=True),
                call().setncatts({'a1': 'A1', 'a2': 'A2', 'missing_value': 'fv8', 'grid_mapping': 'gm'}),
                call().__setitem__(slice(None, None, None), 'data'),
                ]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

if __name__ == "__main__":
    unittest.main()
