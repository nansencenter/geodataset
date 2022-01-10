import os

import numpy as np
import pyproj

from geodataset.geodataset import GeoDatasetRead, GeoDatasetWrite
from geodataset.projection_info import ProjectionInfo
from geodataset.utils import InvalidDatasetError

class CustomDatasetRead(GeoDatasetRead):
    _filename_prefix = None
    _filename_suffix = '.nc'
    def _check_input_file(self):
        n = os.path.basename(self.filename)
        if not (n.startswith(self._filename_prefix) and 
                n.endswith(self._filename_suffix)):
            raise InvalidDatasetError


class Dist2Coast(CustomDatasetRead):
    _filename_prefix = 'dist2coast_4deg.nc'
    lonlat_names = 'lon', 'lat'
    def get_lonlat_arrays(self):
        return np.meshgrid(self['lon'][:], self['lat'][:])


class CmemsMetIceChart(CustomDatasetRead):
    _filename_prefix = 'ice_conc_svalbard_'
    lonlat_names = 'lon', 'lat'


class NerscSarProducts(CustomDatasetRead):
    lonlat_names = 'absent', 'absent'
    def get_lonlat_arrays(self):
        x_grd, y_grd = np.meshgrid(self['x'][:], self['y'][:])
        return self.projection.transform(
            x_grd, y_grd, direction=pyproj.enums.TransformDirection.INVERSE)
    

class NerscDeformation(NerscSarProducts):
    _filename_prefix = 'arctic_2km_deformation_'


class NerscIceType(NerscSarProducts):
    _filename_prefix = 'arctic_2km_icetype_'


class JaxaAmsr2IceConc(CustomDatasetRead):
    _filename_prefix = 'Arc_'
    _filename_suffix = '_res3.125_pyres.nc'
    lonlat_names = 'longitude', 'latitude'


class Etopo(CustomDatasetRead):
    _filename_prefix = 'ETOPO_Arctic_'

    def get_lonlat_arrays(self):
        lon, lat = super().get_lonlat_arrays()
        return np.meshgrid(lon, lat)


class SmosIceThickness(CustomDatasetRead):
    _filename_prefix = 'SMOS_Icethickness_v3.2_north'

    def _get_area_definition(self):
        # TODO:
        # read EXTENT from given X, Y variables
        # read or set units
        # set projection
        # set area definition
        pass


class NetcdfArcMFC(GeoDatasetWrite):
    """ wrapper for netCDF4.Dataset with info about ArcMFC products """
    
    def __init__(self, *args, **kwargs):
        """
        init the object and adds some default parameters which can be overridden by child classes

        Parameters:
        -----------
        args and kwargs for netCDF4.Dataset

        Sets:
        -----
        projection : ProjectionInfo
        projection_names : tuple(str)

        Other attributes are defaults for the parent class NetcdfIO
        """
        super().__init__(*args, **kwargs)
        self.projection_names = ('stereographic', 'polar_stereographic')
        self.projection = ProjectionInfo.topaz_np_stere()

