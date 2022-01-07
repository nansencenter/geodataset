import os
from geodataset.geodataset import GeoDatasetRead, GeoDatasetWrite
from geodataset.projection_info import ProjectionInfo
from geodataset.utils import InvalidDataset

class CustomDatasetRead(GeoDatasetRead):
    _filename_prefix = None
    _filename_suffix = '.nc'
    def _check_input_file(self):
        n = os.path.basename(self.filename)
        if not (n.startswith(self._filename_prefix) and 
                n.endswith(self._filename_suffix)):
            raise InvalidDataset


class CmemsMetIceChart(CustomDatasetRead):
    _filename_prefix = 'ice_conc_svalbard_'

    def _get_lonlat_names(self):
        return 'lon', 'lat'


class NerscSarProducts(CustomDatasetRead):
    pass
    def _get_lonlat_names(self):
        return 'absent', 'absent'
    

class NerscDeformation(NerscSarProducts):
    _filename_prefix = 'arctic_2km_deformation_'


class NerscIceType(GeoDatasetRead):
    _filename_prefix = 'arctic_2km_icetype_'


class JaxaAmsr2IceConc(GeoDatasetRead):
    _filename_prefix = 'Arc_'
    _filename_suffix = '_res3.125_pyres.nc'
    
    def _get_lonlat_names(self):
        return 'longitude', 'latitude'


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

