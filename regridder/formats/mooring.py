from .geodataset import NoneStandardGeoDataset
class Mooring(NoneStandardGeoDataset):
    def __init__(self, file_path):
        self.name_of_longitude_in_netcdf = 'longitude'
        self.name_of_latitude_in_netcdf = 'latitude'
        self.name_of_x_in_netcdf_dimensions = "x"
        self.name_of_y_in_netcdf_dimensions = "y"
        #x[-1, 0] is the lower left corner of x
        self.first_index_of_lower_left_corner = -1
        self.second_index_of_lower_left_corner = 0
        #x[0, -1] is the upper right corner of x
        self.first_index_of_upper_right_corner = 0
        self.second_index_of_upper_right_corner = -1
        super().__init__(file_path)
