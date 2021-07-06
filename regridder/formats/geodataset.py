from datetime import datetime

import numpy as np
import pyproj
from netCDF4 import Dataset
from pyresample.geometry import AreaDefinition
from pyresample.utils import load_cf_area
from time_helpers import get_time_converter, get_time_name
from variable_helpers import exchange_names, var_object
from exceptions import BadAreaDefinition

class GeoDataset():
    def __init__(self, file_path):
        self.file_path = file_path
        self._load_area()

    def _load_area(self):
        """self.area is set in this method, either by use of pyresample functionality (load_cf_area)"""
        try:
            self.area, _ = load_cf_area(self.file_path)
        except ValueError:
            raise BadAreaDefinition

    def get_var(self, vblname, time_index=None,
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

    def nearestDate(self, pivot):
        """
        dto,time_index = self.nearestDate(dto0)
        dto0  = datetime.datetime object
        dto    = datetime.datetime object - nearest value in self.datetimes to dto0
        time_index: dto=self.datetimes[time_index]
        """
        dto        = min(self.datetimes, key=lambda x: abs(x - pivot))
        time_index = self.datetimes.index(dto)
        return dto, time_index


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
