import os
import re
import datetime as dt

import numpy as np
import pyproj

from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError


class ArcMFCModelFile(GeoDatasetRead):
    """
    geodataset for ArcMFC model files

    filenames vary from product to product so just inherit from GeoDatasetRead
    and set projection (not always correctly set in the netcdf files) (OK in some products but not all)
    but don't set filename pattern
    """
    grid_mapping = pyproj.CRS.from_proj4(
        '+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-45 +x_0=0 +y_0=0'
        ' +R=6378273 +ellps=sphere +units=m +no_defs'), 'absent'


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


class Etopo(CustomDatasetRead):
    pattern = re.compile(r'ETOPO_Arctic_\d{1,2}arcmin.nc')


class JaxaAmsr2IceConc(CustomDatasetRead):
    pattern = re.compile(r'Arc_\d{8}_res3.125_pyres.nc')
    lonlat_names = 'longitude', 'latitude'
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'


class NERSCProductBase(CustomDatasetRead):
    lonlat_names = 'absent', 'absent'

    def get_lonlat_arrays(self, ij_range=(None,None,None,None), **kwargs):
        """
        Return lon,lat as 2D arrays

        Parameters
        ----------
        ij_range : tuple(int)
            - [i0, i1, j0, j1]
            - pixel indices for subsetting
            - return lon[i0:i1+1,j0:j1+1], lat[i0:i1+1,j0:j1+1]
                instead of full arrays
        dummy kwargs

        Returns
        -------
        lon : numpy.ndarray
            2D array with longitudes of pixel centers
        lat : numpy.ndarray
            2D array with latitudes of pixel centers
        """
        i0, i1, j0, j1 = ij_range
        x_grd, y_grd = np.meshgrid(self['x'][j0:j1], self['y'][i0:i1])
        return self.projection(x_grd, y_grd, inverse=True)


class NERSCDeformation(NERSCProductBase):
    pattern = re.compile(r'arctic_2km_deformation_\d{8}T\d{6}.nc')


class NERSCIceType(NERSCProductBase):
    pattern = re.compile(r'arctic_2km_icetype_\d{8}T\d{6}.nc')


class NERSCSeaIceAge(NERSCProductBase):
    pattern = re.compile(r'arctic25km_sea_ice_age_v2p1_\d{8}.nc')


class OsisafDriftersNextsim(CustomDatasetRead):
    pattern = re.compile(r'OSISAF_Drifters_.*.nc')
    grid_mapping = pyproj.CRS.from_proj4(
        " +proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        " +a=6378273 +b=6356889.44891 "), 'absent'
    is_lonlat_2d = False


class SmosIceThickness(CustomDatasetRead):
    pattern = re.compile(r'SMOS_Icethickness_v3.2_north_\d{8}.nc')
    grid_mapping = pyproj.CRS.from_epsg(3411), 'absent'


class UniBremenAlbedoMPF(CustomDatasetRead):

    grid_mapping = (pyproj.CRS.from_proj4(
            '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +x_0=0 +y_0=0 '
            '+ellps=WGS84 +units=m +no_defs'), 'absent')
    pattern = re.compile(r'mpd1_\d{8}.nc')

    @staticmethod
    def get_xy_arrays(ij_range=(None,None,None,None), **kwargs):
        """
        Grid info from
        https://nsidc.org/data/polar-stereo/ps_grids.html
        see table 6

        Parameters:
        -----------
        ij_range : tuple(int)
            - [i0, i1, j0, j1]
            - pixel indices for subsetting
            - return x[i0:i1+1,j0:j1+1], y[i0:i1+1,j0:j1+1]
                instead of full arrays
        dummy kwargs

        Returns:
        --------
        x : numpy.ndarray
            2D array with x coordinates of pixel centers
        y : numpy.ndarray
            2D array with y coordinates of pixel centers
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
        px, py = np.meshgrid(
                .5e3 * (qx[:-1] + qx[1:]),
                .5e3 * (qy[:-1] + qy[1:]),
                )
        i0, i1, j0, j1 = ij_range
        return px[i0:i1,j0:j1], py[i0:i1,j0:j1]

    def get_lonlat_arrays(self, **kwargs):
        """
        Parameters:
        -----------
        kwargs for UniBremenAlbedoMPF.get_xy_arrays

        Returns:
        --------
        lon : numpy.ndarray
            2D array
        lat : numpy.ndarray
            2D array
        """
        return self.projection(
                *self.get_xy_arrays(**kwargs), inverse=True)

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
        datestr = bname.split('_')[1][:8]
        return [dt.datetime.strptime(datestr, '%Y%m%d')
                + dt.timedelta(hours=12)]
