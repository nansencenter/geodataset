import glob
import os
import unittest

import pyproj

from geodataset.tools import open_netcdf
from geodataset.tests.base_for_tests import BaseForTests
from geodataset.custom_geodataset import UniBremenAlbedoMPF


class ToolsTests(BaseForTests):

    nc_files = glob.glob(os.path.join(os.environ['TEST_DATA_DIR'], "*.nc"))

    def test_open_netcdf(self):
        for nc_file in self.nc_files:
            with self.subTest(nc_file=nc_file):
                with open_netcdf(nc_file) as ds:
                    self.assertIsInstance(ds.variable_names, list)
                    self.assertIsInstance(ds.variable_names[0], str)
                    if ds.__class__ == UniBremenAlbedoMPF:
                        # files don't contain lon,lat
                        # - get_lonlat_arrays implemented manually
                        continue
                    print(nc_file, ds.lonlat_names)
                    self.assertIsInstance(ds.lonlat_names[0], str)
                    self.assertIsInstance(ds.lonlat_names[1], str)

    def test_get_lonlat_arrays(self):
        for nc_file in self.nc_files:
            with self.subTest(nc_file=nc_file):
                with open_netcdf(nc_file) as ds:
                    if not ds.is_lonlat_2d:
                        # skip for eg OsisafDriftersNextsim (lon,lat are 3d, depending on time also)
                        continue
                    lon, lat = ds.get_lonlat_arrays()
                print(nc_file, len(lon.shape))
                self.assertEqual(len(lon.shape), 2)
                self.assertEqual(len(lat.shape), 2)
                self.assertGreaterEqual(lon.min(), -180)
                self.assertLessEqual(lon.max(), 180)
                self.assertGreaterEqual(lat.min(), -90)
                self.assertLessEqual(lat.max(), 90)

    def test_projection(self):
        for nc_file in self.nc_files:
            with self.subTest(nc_file=nc_file):
                with open_netcdf(nc_file) as ds:
                    self.assertIsInstance(ds.grid_mapping_variable, str)
                    self.assertIsInstance(ds.projection, pyproj.Proj)



if __name__ == "__main__":
    unittest.main()
