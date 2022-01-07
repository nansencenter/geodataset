import os
from geodataset.geodataset import GeoDatasetRead, GeoDatasetWrite
from geodataset.projection_info import ProjectionInfo
from geodataset.utils import InvalidDataset

class CmemsMetIceChart(GeoDatasetRead):
    def _check_input_file(self):
        if not os.path.basename(self.filename).startswith('ice_conc_svalbard_'):
            raise InvalidDataset
    
    def _get_lonlat_names(self):
        return 'lon', 'lat'


class NerscDeformation(GeoDatasetRead):
    def _check_input_file(self):
        if not os.path.basename(self.filename).startswith('arctic_2km_deformation_'):
            raise InvalidDataset
    
    def _get_lonlat_names(self):
        return 'absent', 'absent'


class NerscIceType(GeoDatasetRead):
    def _check_input_file(self):
        if not os.path.basename(self.filename).startswith('arctic_2km_icetype_'):
            raise InvalidDataset
    
    def _get_lonlat_names(self):
        return 'absent', 'absent'


class JaxaAmsr2IceConc(GeoDatasetRead):
    def _check_input_file(self):
        base = os.path.basename(self.filename)
        if not (base.startswith('Arc_') and base.endswith('_res3.125_pyres.nc')):
            raise InvalidDataset
    
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

