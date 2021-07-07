from os.path import basename

from exceptions import BadAreaDefinition

from .geodataset import CustomAreaDefinitionBase, GeoDataset


class Moorings(GeoDataset):
    def _load_area(self):
        if not basename(self.file_path).startswith("Moorings"):
            raise BadAreaDefinition
        try:
            o = MooringAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = o.get_area()
        del o


class MooringAreaDefinition(CustomAreaDefinitionBase):
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
