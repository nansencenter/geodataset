import numpy as np
import pyproj
import pyresample
from netCDF4 import Dataset
from pyresample import bilinear
from pyresample.geometry import AreaDefinition
from pyresample.utils import load_cf_area


class Projection:
    pass


class Interpolator:

    def __init__(self, source_class, source, target_class, target):
        self.source = source_class(source)
        self.target = target_class(target)
        self.source.charaterize()
        self.target.charaterize()
        self.source_data = self.source.nc_dataset
        self.target_data = self.target.nc_dataset
        # new interface is created in above lines, there is no need to hold the previous one anymore
        del self.source.nc_dataset
        del self.target.nc_dataset

    def slice_source(self, variable_name, slices_list):
        return self.slice(self.source_data, variable_name, slices_list)

    def slice_target(self, variable_name, slices_list):
        return self.slice(self.target_data, variable_name, slices_list)

    def slice(self, data, variable_name, slices_list):
        desired_slice=[
            slice(*slice_three_numbers) for slice_three_numbers in slices_list if slice_three_numbers
                      ]
        return np.squeeze(data[variable_name][desired_slice])

class GridGridInterpolator(Interpolator): #(pyresample)

    def __call__(self, variable, method, **kwargs):
        self.resampler = method(self.source.area, self.target.area, **kwargs)
        return self.resampler.resample(variable)


class MeshGridInterpolator(Interpolator):#(Bamg)
    pass
    def __call__(self):
        pass

class GridMeshInterpolator(Interpolator):#(griddata or else)
    pass
    def __call__(self):
        pass

class GeoDataset():
    def __init__(self, file_path):
        self.file_path = file_path

    def find_proj4_string(self):
        self.proj4_string = '+proj=stere +a=6378273.0 +b=6356889.448910593 +lat_0=90 +lat_ts=60 +lon_0=-45'

    def instantiate_pyproj_based_on_proj4_string(self):
        self.proj = pyproj.Proj(self.proj4_string)

    def set__nc_dataset__with_netcdf_python_module(self):
        self.nc_dataset = Dataset(self.file_path)

    def find_x_and_y_for_lower_left_pixel(self):
        """x and y for lower left pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        self.x_ll, self.y_ll = self.proj(
            self.nc_dataset[self.name_of_longitude_in_netcdf][self.first_index_of_lower_left_corner,
                                                              self.second_index_of_lower_left_corner],
            self.nc_dataset[self.name_of_latitude_in_netcdf][self.first_index_of_lower_left_corner,
                                                             self.second_index_of_lower_left_corner]
                                        )#lower left corner

    def find_x_and_y_for_upper_right_pixel(self):
        """x and y for upper right pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        self.x_ur, self.y_ur = self.proj(
            self.nc_dataset[self.name_of_longitude_in_netcdf][self.first_index_of_upper_right_corner,
                                                              self.second_index_of_upper_right_corner],
            self.nc_dataset[self.name_of_latitude_in_netcdf][self.first_index_of_upper_right_corner,
                                                             self.second_index_of_upper_right_corner]
                                        )#upper right corner


    def calculate_number_of_cells_and_shape(self):
        """calculate number of cells and shape"""
        self.number_of_cells_x = self.nc_dataset.dimensions[self.name_of_x_in_netcdf_dimensions].size
        self.number_of_cells_y = self.nc_dataset.dimensions[self.name_of_y_in_netcdf_dimensions].size
        self.shape = (self.number_of_cells_y, self.number_of_cells_x)

    def calculate_corner_and_extent(self):
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

    def set_area_id(self):
        self.area_id = 'id for '+self.__class__.__name__+' object'

    def define_area(self):
        self.area = AreaDefinition.from_extent(self.area_id, self.proj4_string, self.shape, self.area_extent)

    def delete_unecessary_properties_needed_for_area_definition(self):
        del self.proj
        del self.x_ll
        del self.y_ll
        del self.x_ur
        del self.y_ur
        del self.number_of_cells_x
        del self.number_of_cells_y
        del self.scene_length_x
        del self.scene_length_y
        del self.cell_size_x
        del self.cell_size_y
        del self.x_corner_ll
        del self.x_corner_ur
        del self.y_corner_ll
        del self.y_corner_ur
        del self.area_extent
        del self.shape
        del self.area_id

    def charaterize(self):
        """self.area is set in this method, either by use of pyresample functionality (load_cf_area)
        or by costumized area definition in 'except' part of this function. Only self.area and
        self.nc_dataset remain at the end of this function as interface for further calculation."""
        self.set__nc_dataset__with_netcdf_python_module()
        try:
            self.area, _ = load_cf_area(self.file_path)
        except ValueError:
            self.find_proj4_string()
            self.instantiate_pyproj_based_on_proj4_string()
            self.find_x_and_y_for_lower_left_pixel()
            self.find_x_and_y_for_upper_right_pixel()
            self.calculate_number_of_cells_and_shape()
            self.calculate_corner_and_extent()
            self.set_area_id()
            self.define_area()
            self.delete_unecessary_properties_needed_for_area_definition()


class Mooring(GeoDataset):
    def __init__(self, file_path):
        super().__init__(file_path)
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



def main():

    ggi = GridGridInterpolator(Mooring, '/workspaces/Regridder/regridder/Moorings_2021d179.nc',
                               GeoDataset, '/workspaces/Regridder/regridder/ice_conc_nh_polstere-100_multi_202106131200.nc')
    #for slicing, slices should be given as a list of 'three number set'
    cons_from_nc_file = ggi.slice_source('sic', [[0,1],[],[], []])
    resampled_data_cons = ggi(cons_from_nc_file, bilinear.NumpyBilinearResampler, radius_of_influence=15000)

if __name__ == "__main__":
    main()
