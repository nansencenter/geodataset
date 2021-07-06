from .geodataset import CustomAreaDefinitionBase, GeoDataset


class Moorings(GeoDataset):
    def _load_area(self):
        MooringAreaDefinitionObject = MooringAreaDefinition(self.file_path)
        self.area = MooringAreaDefinitionObject._define_area()
        del MooringAreaDefinitionObject


class MooringAreaDefinition(CustomAreaDefinitionBase):
    def __init__(self, file_path):
        self.lon_name = 'longitude'
        self.lat_name = 'latitude'
        self.name_of_x_in_netcdf_dimensions = "x"
        self.name_of_y_in_netcdf_dimensions = "y"
        #x[-1, 0] is the lower left corner of x
        self.ll_row = -1
        self.ll_col = 0
        #x[0, -1] is the upper right corner of x
        self.ur_row = 0
        self.ur_col = -1
        super().__init__(file_path)


    def _calculate_corner_and_extent(self):
        """calculate corner and extent"""
        self.scene_length_x = self.x_ur - self.x_ll
        self.scene_length_y = self.y_ll - self.y_ur
        self.cell_size_x = self.scene_length_x/(self.number_of_cells_x - 1)
        self.cell_size_y = self.scene_length_y/(self.number_of_cells_y - 1)

        self.x_corner_ll = self.x_ll - self.cell_size_x/2
        self.x_corner_ur = self.x_ur + self.cell_size_x/2
        self.y_corner_ll = self.y_ll - self.cell_size_y/2
        self.y_corner_ur = self.y_ur + self.cell_size_y/2
        self.area_extent = (self.x_corner_ll, self.y_corner_ll, self.x_corner_ur, self.y_corner_ur)
