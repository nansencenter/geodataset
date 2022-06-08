import os
import re
import datetime as dt

import numpy as np
import pyproj

from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError

class CustomDatasetRead(GeoDatasetRead):
    pattern = None
    def _check_input_file(self):
        n = os.path.basename(self.filename)
        if not self.pattern.match(n):
            raise InvalidDatasetError


class CmemsMetIceChart(CustomDatasetRead):
    pattern = re.compile(r'ice_conc_svalbard_\d{12}.nc')
    lonlat_names = 'lon', 'lat'


class Dist2Coast(CustomDatasetRead):
    pattern = re.compile(r'dist2coast_4deg.nc')
    lonlat_names = 'lon', 'lat'
    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class Etopo(CustomDatasetRead):
    pattern = re.compile(r'ETOPO_Arctic_\d{1,2}arcmin.nc')

    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class JaxaAmsr2IceConc(CustomDatasetRead):
    pattern = re.compile(r'Arc_\d{8}_res3.125_pyres.nc')
    lonlat_names = 'longitude', 'latitude'
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'


class NerscSarProducts(CustomDatasetRead):
    lonlat_names = 'absent', 'absent'
    def get_lonlat_arrays(self):
        x_grd, y_grd = np.meshgrid(self['x'][:], self['y'][:])
        return self.projection(x_grd, y_grd, inverse=True)
    

class NerscDeformation(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_deformation_\d{8}T\d{6}.nc')


class NerscIceType(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_icetype_\d{8}T\d{6}.nc')


class OsisafDriftersNextsim(CustomDatasetRead):
    pattern = re.compile(r'OSISAF_Drifters_.*.nc')
    grid_mapping = pyproj.CRS.from_proj4(
        " +proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        " +a=6378273 +b=6356889.44891 "), 'absent'
    is_lonlat_2d = False


class SmosIceThickness(CustomDatasetRead):
    pattern = re.compile(r'SMOS_Icethickness_v3.2_north_\d{8}.nc')
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'


class UniBremenMERISAlbedoMPFBase(CustomDatasetRead):

    grid_mapping = (pyproj.CRS.from_proj4(
            '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +x_0=0 +y_0=0 '
            '+ellps=WGS84 +units=m +no_defs'), 'absent')

    @staticmethod
    def get_xy_arrays():
        """
        Grid info from
        https://nsidc.org/data/polar-stereo/ps_grids.html
        see table 6
        """
        x0 = -3850.
        x1 = 3750.
        nx = 608
        y1 = 5850.
        y0 = -5350
        ny = 896

        # get corner points
        qx = np.linspace(x0, x1, nx + 1)
        qy = np.linspace(y0, y1, ny + 1)

        # convert to grid of mid points
        return np.meshgrid(
                .5e3 * (qx[:-1] + qx[1:]),
                .5e3 * (qy[:-1] + qy[1:]),
                )

    def get_lonlat_arrays(self):
        return self.projection(
                *self.get_xy_arrays(), inverse=True)

    @property
    def datetimes(self):
        """
        Get datetimes manually from filename

        Returns:
        --------
        datetimes : list(datetime.datetime)
            all the time values converted to datetime objects
        """
        bname = os.path.basename(self.filepath())
        return [dt.datetime.strptime(bname[4:12], '%Y%m%d')]


class UniBremenMERISAlbedoMPFPre2021(UniBremenMERISAlbedoMPFBase):
    """ older filename format """
    pattern = re.compile(r'mpd_\d{8}.nc')


class UniBremenMERISAlbedoMPF(UniBremenMERISAlbedoMPFBase):
    """ after 2021 filenames have _NR suffix """
    pattern = re.compile(r'mpd_\d{8}_NR.nc')
