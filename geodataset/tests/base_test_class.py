import os

from unittest import TestCase

class GeodatasetTestBase(TestCase):

    def setUp(self):
        self.osisaf_filename = os.path.join(os.environ['TEST_DATA_DIR'], "ice_drift_nh_polstere-625_multi-oi_202201011200-202201031200.nc")
        self.osisaf_var = 'dX'
        self.osisaf_units = 'km'
        self.osisaf_std_name = 'sea_ice_x_displacement'
        self.osisaf_max = 49.51771
        self.moorings_filename = os.path.join(os.environ['TEST_DATA_DIR'], "Moorings.nc")
        self.moorings_var = 'sic'
