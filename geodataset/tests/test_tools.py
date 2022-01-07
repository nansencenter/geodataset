import glob
import os
import unittest

from geodataset.tools import open_netcdf

from geodataset.tests.base_for_tests import BaseForTests

class ToolsTests(BaseForTests):
    def setUp(self):
        super().setUp()
        self.nc_files = glob.glob(os.path.join(os.environ['TEST_DATA_DIR'], "*.nc"))

    def test_open_netcdf(self):
        for nc_file in self.nc_files:
            ds = open_netcdf(nc_file)
            print(nc_file, ds.lonlat_names)
            self.assertIsInstance(ds.lonlat_names[0], str)
            self.assertIsInstance(ds.lonlat_names[1], str)

    def test_get_lonlat_arrays(self):
        for nc_file in self.nc_files:
            ds = open_netcdf(nc_file)
            lon, lat = ds.get_lonlat_arrays()
            print(nc_file, len(lon.shape))
            self.assertEqual(len(lon.shape), 2)
            self.assertEqual(len(lat.shape), 2)

if __name__ == "__main__":
    unittest.main()
