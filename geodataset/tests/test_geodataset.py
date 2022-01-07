import glob
import os
import numpy as np
import unittest
import datetime as dt
from mock import patch, call, Mock, MagicMock, DEFAULT
import subprocess

from geodataset.geodataset import GeoDatasetBase, GeoDatasetWrite, GeoDatasetRead, Dataset, ProjectionInfo
from geodataset.utils import InvalidDataset
from geodataset.tests.base_for_tests import BaseForTests

class GeodatasetTestBase(BaseForTests):
    def setUp(self):
        super().setUp()
        self.osisaf_filename = os.path.join(os.environ['TEST_DATA_DIR'], "ice_drift_nh_polstere-625_multi-oi_202201011200-202201031200.nc")
        self.osisaf_var = 'dX'
        self.osisaf_units = 'km'
        self.osisaf_std_name = 'sea_ice_x_displacement'
        self.osisaf_max = 49.51771
        self.moorings_filename = os.path.join(os.environ['TEST_DATA_DIR'], "Moorings.nc")
        self.moorings_var = 'sic'

class GeoDatasetBaseTest(GeodatasetTestBase):
    @patch.multiple(GeoDatasetBase, __init__=MagicMock(return_value=None), variables=DEFAULT,
            is_lonlat_dim=DEFAULT)
    def test_get_xy_dims_from_lonlat_1(self, **kwargs):
        lon = np.random.normal(size=(2,2))
        lat = np.random.normal(size=(2,2))
        nc = GeoDatasetBase()
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

    @patch.multiple(GeoDatasetBase, __init__=MagicMock(return_value=None), variables=DEFAULT)
    @patch('geodataset.geodataset.vars')
    def test_convert_time_data(self, mock_vars, **kwargs):
        shp = (4,2)
        tdata = 1333195200*np.ones(shp)
        dto = dt.datetime(2020, 3, 31, 12)
        nc = GeoDatasetBase()
        nc.time_name = 'time_name'
        mock_vars.return_value = dict(units='seconds since 1978-01-01 00:00:00', calendar='standard')
        nc.variables = dict(time_name='ncvar')

        dtimes = nc.convert_time_data(tdata)
        mock_vars.assert_called_with('ncvar')
        self.assertEqual(shp, dtimes.shape)
        self.assertTrue(np.all(dtimes==dto))
        self.assertIsInstance(dtimes, np.ndarray)


class GeoDatasetWriteTest(GeodatasetTestBase):
    @patch.multiple(GeoDatasetWrite, __init__=MagicMock(return_value=None), dimensions=DEFAULT)
    def test_is_lonlat_dim(self, **kwargs):
        nc = GeoDatasetWrite()
        nc.lonlat_names = ('lon', 'lat')
        nc.dimensions = ('x', 'y')
        self.assertFalse(nc.is_lonlat_dim)
        nc.dimensions = ('lon', 'lat')
        self.assertTrue(nc.is_lonlat_dim)

    @patch.multiple(GeoDatasetWrite, __init__=MagicMock(return_value=None), convert_time_data=DEFAULT, variables=DEFAULT)
    def test_datetimes(self, **kwargs):
        nc = GeoDatasetWrite()
        nc.time_name = 'time_name'
        tdata = np.random.uniform(size=(3,))
        nc.variables = dict(time_name=tdata)
        kwargs['convert_time_data'].side_effect = lambda x:2*x

        dtimes = nc.datetimes
        self.assert_lists_equal(list(2*tdata), dtimes)
        self.assert_mock_has_calls(kwargs['convert_time_data'], [call(tdata)])

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None), createVariable=DEFAULT)
    def test_set_projection_variable(self, **kwargs):
        nc = GeoDatasetWrite()
        nc.projection_names = ('gm', 'gmn')
        nc.projection = MagicMock()
        nc.projection.ncattrs = MagicMock(return_value='ncatts')
        nc.set_projection_variable()

        nc.projection.ncattrs.assert_called_once_with('gmn')
        req_calls = [call('gm', 'i1'), call().setncatts('ncatts'),
                call().setncatts({'proj4': '+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-45 +x_0=0 +y_0=0 +R=6378273 +ellps=sphere +units=m +no_defs'})]
        self.assert_mock_has_calls(kwargs['createVariable'], req_calls)

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None),
            createDimension=DEFAULT,
            createVariable=DEFAULT,
            )
    def test_set_xy_dims(self, **kwargs):
        nx = 2
        ny = 3
        x = np.random.normal(size=(nx,))
        y = np.random.normal(size=(ny,))

        nc = GeoDatasetWrite()
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

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    def test_set_lonlat(self, **kwargs):

        slon = (2,2)
        slat = (3,3)
        lon = np.random.normal(size=slon)
        lat = np.random.normal(size=slat)

        nc = GeoDatasetWrite()
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

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None),
            createDimension=DEFAULT,
            createVariable=DEFAULT,
            )
    def test_set_time_variables_dimensions(self, **kwargs):
        nc = GeoDatasetWrite()
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

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    @patch('geodataset.geodataset.np.double')
    @patch('geodataset.geodataset.np.float32')
    def test_set_variable_1(self, f4, f8, **kwargs):
        ''' test f4 with _FillValue defined '''
        nc = GeoDatasetWrite()
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

    @patch.multiple(GeoDatasetWrite,
            __init__=MagicMock(return_value=None),
            createVariable=DEFAULT,
            )
    @patch('geodataset.geodataset.np.double')
    @patch('geodataset.geodataset.np.float32')
    def test_set_variable_2(self, f4, f8, **kwargs):
        ''' test f8 with missing_value defined '''
        nc = GeoDatasetWrite()
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


class GeoDatasetReadTest(GeodatasetTestBase):
    def test_init(self):
        with Dataset(self.osisaf_filename, 'r') as ds:
            with GeoDatasetRead(self.osisaf_filename, 'r') as nc:
                self.assertEqual(ds.ncattrs(), nc.ncattrs())
                self.assertEqual(list(ds.dimensions), list(nc.dimensions))
                self.assertEqual(list(ds.variables), list(nc.variables))
                self.assertEqual(vars(nc.projection), vars(ProjectionInfo()))
                self.assertEqual(nc.projection_names, 
                ('Polar_Stereographic_Grid', 'polar_stereographic'))
                self.assertEqual(nc.spatial_dim_names, ('x', 'y'))
                self.assertEqual(nc.lonlat_names, ('lon', 'lat'))
                self.assertEqual(nc.time_name, 'time')
                self.assertFalse(nc.is_lonlat_dim)

    def test_method_get_nearest_date(self):
        """Test the ability of finding the nearest date to a specific date. 2007 is near to 2006 (in
        netcdf file) than the 2010."""
        with GeoDatasetRead(self.osisaf_filename, 'r') as ds:
            #ds.datetimes.append(dt.datetime(2000, 1, 1, 12, 0))
            ans, ans_index = ds.get_nearest_date(dt.datetime(2020, 1, 1, 12, 0))
            self.assertEqual(ans, dt.datetime(2022, 1, 3, 12, 0))
            self.assertEqual(ans_index, 0)

    def test_get_var_names(self):
        """Test the ability of finding the nearest date to a specific date. 2007 is near to 2006 (in
        netcdf file) than the 2010."""
        with GeoDatasetRead(self.osisaf_filename, 'r') as ds:
            var_names = ds._get_variable_names()
            self.assertEqual(var_names, 
            ['lat', 'lon', 'dt0', 'lon1', 'lat1', 'dt1',
            'dX', 'dY', 'status_flag', 'uncert_dX_and_dY'])

    def test_get_variable_array(self):
        with GeoDatasetRead(self.osisaf_filename, 'r') as ds:
            a = ds.get_variable_array('dX')
            b = ds.get_variable_array('lon')
        self.assertEqual(a.shape, (177, 119))
        self.assertEqual(b.shape, (177, 119))

    def test_get_lonlat_arrays(self):
        with GeoDatasetRead(self.osisaf_filename, 'r') as ds:
            lon, lat = ds.get_lonlat_arrays()
        self.assertEqual(len(lon.shape), 2)
        self.assertEqual(len(lat.shape), 2)

    @patch.multiple(GeoDatasetRead,
            __init__=MagicMock(return_value=None),
            __exit__=MagicMock(return_value=None),
            variables=DEFAULT,
            )
    def test_get_lonlat_names(self, **kwargs):
        ''' test f4 with _FillValue defined '''
        variables = {
            'lon': Mock(),
            'lat': Mock(),
            'sic': Mock(),
        }
        variables['lon'].ncattrs.return_value = ['standard_name', 'a', 'b']
        variables['lat'].ncattrs.return_value = ['standard_name', 'c', 'd']
        variables['sic'].ncattrs.return_value = ['standard_name', 'c', 'd']
        variables['lon'].standard_name = 'longitude'
        variables['lat'].standard_name = 'latitude'
        variables['sic'].standard_name = 'sea_ice_concentration'
        
        with GeoDatasetRead() as ds:
            ds.variables = variables
            lon_name, lat_name = ds._get_lonlat_names()

        self.assertEqual(lon_name, 'lon')
        self.assertEqual(lat_name, 'lat')

    @patch.multiple(GeoDatasetRead,
            __init__=MagicMock(return_value=None),
            __exit__=MagicMock(return_value=None),
            variables=DEFAULT,
            )
    def test_get_lonlat_names_raises(self, **kwargs):
        ''' test f4 with _FillValue defined '''
        variables = {
            'lon': Mock(),
        }
        variables['lon'].ncattrs.return_value = ['standard_name', 'a', 'b']
        variables['lon'].standard_name = 'longitude'
        
        with GeoDatasetRead() as ds:
            ds.variables = variables
            with self.assertRaises(InvalidDataset):
                lon_name, lat_name = ds._get_lonlat_names()

if __name__ == "__main__":
    unittest.main()
