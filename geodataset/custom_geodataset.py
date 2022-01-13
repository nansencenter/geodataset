import os
import re

import numpy as np
import pyproj

from geodataset.geodataset import GeoDatasetRead, GeoDatasetWrite
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
    grid_mapping_variable = 'crs'

    @property
    def projection(self):
        return pyproj.Proj(self.variables['crs'].proj4_string)


class Dist2Coast(CustomDatasetRead):
    pattern = re.compile(r'dist2coast_4deg.nc')
    lonlat_names = 'lon', 'lat'
    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class Etopo(CustomDatasetRead):
    pattern = re.compile(r'ETOPO_Arctic_\d{1,2}arcmin.nc')

    def get_lonlat_arrays(self):
        lon, lat = super().get_lonlat_arrays()
        return np.meshgrid(lon, lat)


class JaxaAmsr2IceConc(CustomDatasetRead):
    pattern = re.compile(r'Arc_\d{8}_res3.125_pyres.nc')
    lonlat_names = 'longitude', 'latitude'
    projection = pyproj.Proj(3411)
    grid_mapping_variable = 'absent'


class MooringsNextsim(CustomDatasetRead):
    pattern = re.compile(r'Moorings.*.nc')
    projection = pyproj.Proj(
        '+proj=stere +a=6378273.0 +b=6356889.448910593 '
        '+lon_0=-45.0 +lat_0=90.0 +lat_ts=60.0')
    grid_mapping_variable = 'Polar_Stereographic_Grid'


class MooringsArcMfc(CustomDatasetRead):
    pattern = re.compile(r'Moorings.*.nc')
    projection = pyproj.Proj(
        '+proj=stere +a=6378273.0 +b=6378273.0 '
        '+lon_0=-45.0 +lat_0=90.0 +lat_ts=90.0')
    grid_mapping_variable = 'absent'


class NerscSarProducts(CustomDatasetRead):
    lonlat_names = 'absent', 'absent'
    def get_lonlat_arrays(self):
        x_grd, y_grd = np.meshgrid(self['x'][:], self['y'][:])
        return self.projection.transform(
            x_grd, y_grd, direction=pyproj.enums.TransformDirection.INVERSE)
    

class NerscDeformation(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_deformation_\d{8}T\d{6}.nc')


class NerscIceType(NerscSarProducts):
    pattern = re.compile(r'arctic_2km_icetype_\d{8}T\d{6}.nc')


class OsisafDriftersNextsim(CustomDatasetRead):
    pattern = re.compile(r'OSISAF_Drifters_.*.nc')
    projection = pyproj.Proj("+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
     " +a=6378273 +b=6356889.44891 ")
    grid_mapping_variable = 'absent'


class SmosIceThickness(CustomDatasetRead):
    pattern = re.compile(r'SMOS_Icethickness_v3.2_north_\d{8}.nc')
    projection = pyproj.Proj(3411)
    grid_mapping_variable = 'absent'


class Topaz4Forecast(CustomDatasetRead):
    pattern = re.compile(r'\d{8}_dm-metno-MODEL-topaz4-ARC-b\d{8}-fv02.0.nc')
    projection = pyproj.Proj("+proj=stere +lat_0=90 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
    grid_mapping_variable = 'stereographic'


class NetcdfArcMFC(GeoDatasetWrite):
    """ wrapper for netCDF4.Dataset with info about ArcMFC products """
    grid_mapping_variable = 'stereographic'
    projection = pyproj.Proj(
        '+proj=stere +a=6378273 +b=6378273.0 '
        ' +lon_0=-45 +lat_0=90 +lat_ts=90')