import os
import unittest

import numpy as np
import pyproj
import datetime as dt

from geodataset.projection_info import ProjectionInfo

from geodataset.tests.base_for_tests import BaseForTests


class ProjectionInfoTest(BaseForTests):
    def test_default_projection(self):

        # map to x,y with mapx
        #lon, lat = self.lonlat_test
        lon, lat = 10, 10

        # do the same with pyproj map in ProjectionInfo
        proj1 = ProjectionInfo()
        x1, y1 = proj1.pyproj(lon, lat, inverse=False)

        proj2 = ProjectionInfo.init_from_mppfile(mppfile= self.mppfile)
        x2, y2 = proj2.pyproj(lon, lat, inverse=False)
        self.assertEqual(proj1.a,      proj2.a)
        self.assertEqual(proj1.b,      proj2.b)
        self.assertEqual(proj1.lat_0,  proj2.lat_0)
        self.assertEqual(proj1.lon_0,  proj2.lon_0)
        self.assertEqual(proj1.lat_ts, proj2.lat_ts)

        proj3 = ProjectionInfo.init_from_mppfile(mppfile=None)
        self.assertEqual(proj1.a,      proj3.a)
        self.assertEqual(proj1.b,      proj3.b)
        self.assertEqual(proj1.lat_0,  proj3.lat_0)
        self.assertEqual(proj1.lon_0,  proj3.lon_0)
        self.assertEqual(proj1.lat_ts, proj3.lat_ts)

    def test_props_projection(self):
        proj = ProjectionInfo()
        self.assertEqual('stere', proj.proj)
        a, b = proj.earthshape
        self.assertEqual(a, proj.a)
        self.assertEqual(b, proj.b)
        geod = proj.geodesic
        self.assertIsInstance(geod, pyproj.Geod)

    def test_get_eccentricity(self):

        # circle: e = 0
        a = 1
        b = 1
        self.assertEqual(0., ProjectionInfo.get_eccentricity(a, b))

        with self.assertRaises(AssertionError):
            ProjectionInfo.get_eccentricity(a, 2*a)

        # ellipse and integer inputs
        a = 2
        b = 1
        ecc = np.sqrt(1- .25)
        self.assertEqual(ecc, ProjectionInfo.get_eccentricity(a, b))

        # ellipse and float inputs
        a = 2.
        b = 1.
        ecc = np.sqrt(1- .25)
        self.assertEqual(ecc, ProjectionInfo.get_eccentricity(a, b))

    def test_ncattrs(self):
        p = ProjectionInfo.topaz_np_stere()
        atts = p.ncattrs('polar_stereographic')
        self.assertEqual(atts, dict(
            latitude_of_projection_origin = p.lat_0,
            longitude_of_projection_origin = p.lon_0,
            straight_vertical_longitude_from_pole = p.lon_0,
            semi_major_axis = p.a,
            semi_minor_axis = p.b,
            scale_factor_at_projection_origin = p.k_0,
            grid_mapping_name = 'polar_stereographic',
            false_northing = 0.,
            false_easting = 0.,
            proj4 = p.pyproj.srs,
            ))

    def test_k_0(self):
        p = ProjectionInfo.topaz_np_stere()
        self.assertTrue(self.floats_equal(p.k_0, 1.))

if __name__ == "__main__":
    unittest.main()
