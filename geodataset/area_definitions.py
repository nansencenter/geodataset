
import pyproj
from netCDF4 import Dataset
from pyresample.geometry import AreaDefinition


class CustomAreaDefinitionBase():
    """class for costimzed manner of reading 'area_defintion'"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.proj = pyproj.Proj(self.proj4_string)
        self._create_area()

    def _create_area(self):
        self._set_corner_coordinates()
        self._set_shape()
        self._set_extent()
        self._set_area_id()

    def _set_corner_coordinates(self):
        """x and y for upper right pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        with Dataset(self.file_path) as nc:
            x, y = self.proj(
                        nc[self.lon_name][[self.ll_row, self.ur_row], [self.ll_col, self.ur_col]],
                        nc[self.lat_name][[self.ll_row, self.ur_row], [self.ll_col, self.ur_col]]
                            )
        #since we passed (in above line) the "ll" the first and then "ur" as the second, the "ur"
        # is always at [1,1] matrix and "ll" is always at [0,0]
        self.x_ur = x[1,1]
        self.x_ll = x[0,0]
        self.y_ur = y[1,1]
        self.y_ll = y[0,0]

    def _set_shape(self):
        """calculate number of cells and shape"""
        with Dataset(self.file_path) as nc:
            self.number_of_cells_x = nc.dimensions[self.name_of_x_in_netcdf_dimensions].size
            self.number_of_cells_y = nc.dimensions[self.name_of_y_in_netcdf_dimensions].size
        self.shape = (self.number_of_cells_y, self.number_of_cells_x)

    def _set_area_id(self):
        self.area_id = 'id for '+self.__class__.__name__+' object'

    def get_area(self):
        return AreaDefinition.from_extent(self.area_id, self.proj4_string, self.shape, self.area_extent)

    def _set_extent(self):
        raise NotImplementedError('The _set_extent() method was not implemented')


class MooringsAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'longitude'
    lat_name = 'latitude'
    name_of_x_in_netcdf_dimensions = "x"
    name_of_y_in_netcdf_dimensions = "y"
    #x[-1, 0] is the lower left corner of x
    ll_row = -1
    ll_col = 0
    #x[0, -1] is the upper right corner of x
    ur_row = 0
    ur_col = -1
    proj4_string = '+proj=stere +a=6378273.0 +b=6356889.448910593 +lat_0=90 +lat_ts=60 +lon_0=-45'

    def _set_extent(self):
        """calculate corner and extent"""
        self.width = self.x_ur - self.x_ll
        self.height = self.y_ll - self.y_ur
        self.cell_size_x = self.width / (self.number_of_cells_x - 1)
        self.cell_size_y = self.height / (self.number_of_cells_y - 1)

        self.x_corner_ll = self.x_ll - self.cell_size_x/2
        self.x_corner_ur = self.x_ur + self.cell_size_x/2
        self.y_corner_ll = self.y_ll - self.cell_size_y/2
        self.y_corner_ur = self.y_ur + self.cell_size_y/2
        self.area_extent = (self.x_corner_ll, self.y_corner_ll, self.x_corner_ur, self.y_corner_ur)
