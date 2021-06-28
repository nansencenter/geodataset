from netCDF4 import Dataset
import pyproj
from pyresample.geometry import AreaDefinition
from pyresample.utils import load_cf_area
from variable_helpers import exchange_names
from variable_helpers import var_object
from time_helpers import get_time_name, get_time_converter
import numpy as np
from datetime import datetime



class GeoDataset():
    def __init__(self, file_path):
        self.file_path = file_path
        self._charaterize()

    def _charaterize(self):
        """self.area is set in this method, either by use of pyresample functionality (load_cf_area)"""
        self.area, _ = load_cf_area(self.file_path)

    def _set__nc_dataset__with_netcdf_python_module(self):
        self.nc_dataset = Dataset(self.file_path)

    def _get_var(self, vblname, time_index=None,
            depth_index=0, ij_range=None, **kwargs):
        """
        vbl=nc_get_var(ncfil, vblname, time_index=None)
        *ncfil is string (filename)
        *vname is string (variable name)
        *time_index is record number to get
        *depth_index is horizon number to get
        *vbl is a mod_reading.var_object instance
        """
        # NB kwargs is not used, but is there as a dummy to avoid having to sort kwargs
        # before calling this function

        #check_names(vname, self.variables)

        with Dataset(self.file_path) as nc:
            vblname = exchange_names(vblname, nc.variables)
            vbl0 = nc.variables[vblname]

            # get the netcdf attributes
            attlist = vbl0.ncattrs()
            attvals = []
            for att in attlist:
                attval = getattr(vbl0, att)
                attvals.append(attval)

            dims  = vbl0.dimensions
            shape = vbl0.shape

            # do we want to limit the range
            if ij_range is not None:
                i0, i1, j0, j1 = ij_range

            # some attributes that depend on rank
            if vbl0.ndim==1:
                vals = vbl0[:]

            elif vbl0.ndim==2:
                if ij_range is not None:
                    vals = vbl0[i0:i1, j0:j1]
                else:
                    vals = vbl0[:, :]

            elif vbl0.ndim==3:
                if time_index is None:
                    if shape[0]==1:
                        time_index = 0
                if time_index is None:
                    if ij_range is not None:
                        vals = vbl0[:, i0:i1, j0:j1]
                    else:
                        vals = vbl0[:, :, :]
                else:
                    if ij_range is not None:
                        vals = vbl0[time_index, i0:i1, j0:j1]
                    else:
                        vals = vbl0[time_index, :, :]
                    dims = dims[1:]

            elif vbl0.ndim==4:
                if time_index is None:
                    if shape[0]==1:
                        time_index = 0

                if time_index is None:
                    if ij_range is not None:
                        vals = vbl0[:, depth_index, i0:i1, j0:j1]
                    else:
                        vals = vbl0[:, depth_index, :, :]
                    dims = (dims[0], dims[2], dims[3])
                else:
                    if ij_range is not None:
                        vals = vbl0[time_index, depth_index, i0:i1, j0:j1]
                    else:
                        vals = vbl0[time_index, depth_index, :, :]
                    dims = dims[2:]


        attlist.append('dimensions')
        attvals.append(dims)
        return var_object(vals, extra_atts=[attlist, attvals])

    def _set_time_info(self):
        """
        * sets self.time_name  = name of time variable
        * sets self.time_dim = True or False - is time is a dimension
        * sets self.time_converter = function to convert time value to datetime
        * sets datetimes
        """
        with Dataset(self.file_path) as nc:
            self.time_name = get_time_name(nc)
            self.time_dim  = (self.time_name is not None)

            if not self.time_dim:
                self.datetimes = None
                return

            time = nc.variables[self.time_name]
            fmt  = '%Y-%m-%d %H:%M:%S'

            self.time_converter = get_time_converter(time)

            arr = time[:] #time values
        self.datetimes  = []
        self.timevalues = []

        Unit = self.time_converter.units.lower()

        for i, tval in enumerate(arr):
            if isinstance(tval, np.int32):
                # can be problems if int32 format
                tval  = int(tval)
            try:
                cdate = self.time_converter.num2date(tval).strftime(fmt)
            except ValueError:
                # might get errors if close to end/start of month
                # eg CS2-SMOS
                tval=round(float(tval))
                cdate = self.time_converter.num2date(tval).strftime(fmt)
            dto    = datetime.strptime(cdate, fmt)         # now a proper datetime object
            self.datetimes.append(dto)

            if i==0:
                self.reftime  = dto

            tdiff = (dto-self.reftime).total_seconds()
            if Unit=='seconds':
                self.timevalues.append(tdiff/3600.)         # convert to hours for readability
                self.timeunits = 'hour'
            elif Unit=='hours':
                self.timevalues.append(tdiff/3600.)         # keep as hours
                self.timeunits = 'hour'
            elif Unit=='days':
                self.timevalues.append(tdiff/3600./24.)    # keep as days
                self.timeunits = 'day'

        self.number_of_time_records = len(self.datetimes)


class NoneStandardGeoDataset(GeoDataset):
    """class for costimzed manner of reading 'area_defintion'"""
    def __init__(self, file_path):
        super().__init__(file_path)

    def _charaterize(self):
        self._set__nc_dataset__with_netcdf_python_module()
        self._find_proj4_string()
        self._instantiate_pyproj_based_on_proj4_string()
        self._find_x_and_y_for_lower_left_pixel()
        self._find_x_and_y_for_upper_right_pixel()
        self._calculate_number_of_cells_and_shape()
        self._calculate_corner_and_extent()
        self._set_area_id()
        self._define_area()
        self._delete_unecessary_properties()

    def _find_proj4_string(self):
        self.proj4_string = '+proj=stere +a=6378273.0 +b=6356889.448910593 +lat_0=90 +lat_ts=60 +lon_0=-45'

    def _instantiate_pyproj_based_on_proj4_string(self):
        self.proj = pyproj.Proj(self.proj4_string)

    def _find_x_and_y_for_lower_left_pixel(self):
        """x and y for lower left pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        self.x_ll, self.y_ll = self._find_x_and_y_of_pixel(self.first_index_of_lower_left_corner,
                                                           self.second_index_of_lower_left_corner)

    def _find_x_and_y_for_upper_right_pixel(self):
        """x and y for upper right pixel is obtained by converting the corresponding corner lat and lon
        into x and y format"""
        self.x_ur, self.y_ur = self._find_x_and_y_of_pixel(self.first_index_of_upper_right_corner,
                                                           self.second_index_of_upper_right_corner)

    def _find_x_and_y_of_pixel(self, first_index, second_index):
        """find x ,y of pixel by pyproj"""
        return self.proj(
            self.nc_dataset[self.name_of_longitude_in_netcdf][first_index, second_index],
            self.nc_dataset[self.name_of_latitude_in_netcdf][first_index, second_index]
                        )


    def _calculate_number_of_cells_and_shape(self):
        """calculate number of cells and shape"""
        self.number_of_cells_x = self.nc_dataset.dimensions[self.name_of_x_in_netcdf_dimensions].size
        self.number_of_cells_y = self.nc_dataset.dimensions[self.name_of_y_in_netcdf_dimensions].size
        self.shape = (self.number_of_cells_y, self.number_of_cells_x)

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

    def _set_area_id(self):
        self.area_id = 'id for '+self.__class__.__name__+' object'

    def _define_area(self):
        self.area = AreaDefinition.from_extent(self.area_id, self.proj4_string, self.shape, self.area_extent)

    def _delete_unecessary_properties(self):
        """after creation of area of object, unecessary properties that are being used for creating
        the area are deleted here."""
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
