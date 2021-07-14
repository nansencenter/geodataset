import pyproj
from netCDF4 import Dataset
from pyresample.geometry import AreaDefinition


class CustomAreaDefinitionBase():
    """class for costimzed manner of reading 'area_defintion'"""
    #x[-1, 0] is the lower left corner of x
    ll_row = -1
    ll_col = 0
    #x[0, -1] is the upper right corner of x
    ur_row = 0
    ur_col = -1
    #x[0, 0] is the upper left corner of x
    ul_row = 0
    ul_col = 0
    #x[-1, -1] is the lower right corner of x
    lr_row = -1
    lr_col = -1

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
        """x and y for corner pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        with Dataset(self.file_path) as nc:
            x, y = self.proj(
                        nc[self.lon_name][
                                            [self.ll_row, self.ur_row, self.lr_row, self.ul_row],
                                            [self.ll_col, self.ur_col, self.lr_col, self.ul_col]
                                         ],
                        nc[self.lat_name][
                                            [self.ll_row, self.ur_row, self.lr_row, self.ul_row],
                                            [self.ll_col, self.ur_col, self.lr_col, self.ul_col]
                                         ]
                            )
        #since we passed (in above line) the "ll" the first and then "ur" as the second, the "ur"
        # is always at [1,1] in the matrix and "ll" is always at [0,0] in the matrix.
        ##since we passed (in above line) the "lr" as the third and then "ul" as the fourth, the "ul"
        ## is always at [3,3] in the matrix and "lr" is always at [2,2] in the matrix
        self.x_ll = x[0, 0]
        self.y_ll = y[0, 0]
        self.x_ur = x[1, 1]
        self.y_ur = y[1, 1]
        self.x_lr = x[2, 2]
        self.y_lr = y[2, 2]
        self.x_ul = x[3, 3]
        self.y_ul = y[3, 3]

    def _set_shape(self):
        """calculate number of cells and shape. If x and y are present in the netcdf file, then the
        size of them is used for shape. Otherwise, the size of lon and lat is used for the shape"""
        with Dataset(self.file_path) as nc:
            self.number_of_points_in_dimension_x = nc.dimensions[self.name_of_x_in_netcdf_dimensions].size
            self.number_of_points_in_dimension_y = nc.dimensions[self.name_of_y_in_netcdf_dimensions].size


        self.shape = (self.number_of_points_in_dimension_y, self.number_of_points_in_dimension_x)

    def _set_area_id(self):
        self.area_id = 'id for '+self.__class__.__name__+' object'

    def get_area(self):
        return AreaDefinition.from_extent(self.area_id, self.proj4_string, self.shape, self.area_extent)

    def _set_extent(self):
        """width and height are calculated in a way that they preserve the 'sign convention' for all
        type of netcdf files. Sign of width and height (correspondingly 'cell_size_x' and
        'cell_size_y') is changing based on the direction of increasing the x and y axis. This sign
        convention is correct for calculating the corners based on the lower-left (ll) pixel and
        upper-right (ur) pixel of data. Pyresample always need ll and ur for extent calculation."""
        self.width = self.x_lr - self.x_ul
        self.height = self.y_lr - self.y_ul
        self.cell_size_x = self.width / (self.number_of_points_in_dimension_x - 1)
        self.cell_size_y = self.height / (self.number_of_points_in_dimension_y - 1)

        self.x_corner_ll = self.x_ll - self.cell_size_x/2
        self.x_corner_ur = self.x_ur + self.cell_size_x/2
        self.y_corner_ll = self.y_ll - self.cell_size_y/2
        self.y_corner_ur = self.y_ur + self.cell_size_y/2
        self.area_extent = (self.x_corner_ll, self.y_corner_ll, self.x_corner_ur, self.y_corner_ur)


class MooringsAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'longitude'
    lat_name = 'latitude'
    name_of_x_in_netcdf_dimensions = "x"
    name_of_y_in_netcdf_dimensions = "y"
    proj4_string = '+proj=stere +a=6378273.0 +b=6356889.448910593 +lat_0=90 +lat_ts=60 +lon_0=-45'



class Topaz4ArcAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'longitude'
    lat_name = 'latitude'
    name_of_x_in_netcdf_dimensions = "x"
    name_of_y_in_netcdf_dimensions = "y"
    proj4_string = '+proj=stere +a=6378273.0  ecc=0. +lat_0=90 +lat_ts=90 +lon_0=-45'


class AMSR2IceConcAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'longitude'
    lat_name = 'latitude'
    name_of_x_in_netcdf_dimensions = "x"
    name_of_y_in_netcdf_dimensions = "y"
    proj4_string = '+proj=stere +a=6378273.0  ecc=0.081816153 +lat_0=90 +lat_ts=70 +lon_0=-45'


class ASRFINALAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'XLONG'
    lat_name = 'XLAT'
    name_of_x_in_netcdf_dimensions = "x"
    name_of_y_in_netcdf_dimensions = "y"
    proj4_string = '+proj=stere +a=6378273.0  ecc=0.081816153 +lat_0=90 +lat_ts=70 +lon_0=-45'


class METNOARCsvalbardAreaDefinition(CustomAreaDefinitionBase):
    lon_name = 'lon'
    lat_name = 'lat'
    name_of_x_in_netcdf_dimensions = "xc"
    name_of_y_in_netcdf_dimensions = "yc"
    proj4_string = '+proj=stere +a=6371000.0  ecc=0.0 +lat_0=90 +lat_ts=90 +lon_0=0'
