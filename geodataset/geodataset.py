import datetime as dt

from netCDF4 import Dataset
import netcdftime
import numpy as np
import pyproj
from pyproj.exceptions import CRSError
from pyresample.utils import load_cf_area
from xarray.core.variable import MissingDimensionsError

from geodataset.utils import InvalidDatasetError
from geodataset.projection_info import ProjectionInfo

class GeoDatasetBase(Dataset):
    """ Abstract wrapper for netCDF4.Dataset for common input or ouput tasks """
    lonlat_names = None
    projection = None
    projection_names = None
    spatial_dim_names = None
    time_name = None

    def __init__(self, *args, **kwargs):
        """
        Initialise the object using netCDF4.Dataset()

        Sets:
        -----
        filename : str
            name of input file
        """
        super().__init__(*args, **kwargs)
        self.filename = args[0]
        self._check_input_file()

    def __setattr__(self, att, val):
        """ set object attributes (not netcdf attributes)
        This method overrides netCDF4.Dataset.__setattr__, which calls netCDF4.Dataset.setncattr """
        self.__dict__[att] = val

    def _check_input_file(self):
        """ Check if input file is valid for the current class or raise InvalidDatasetError """
        pass

    def convert_time_data(self, tdata):
        """
        Convert numeric time values to datetime.datetime objects.
        Uses time units of variable with name self.time_name

        Parameters:
        -----------
        time_num : numpy.ndarray(float)

        Returns:
        --------
        time : numpy.ndarray(datetime.datetime)
        """
        atts = vars(self.variables[self.time_name])
        cal = atts.get('calendar', 'standard')
        units = atts['units']
        datetimes = [netcdftime.num2date(t, units, calendar=cal) for t in tdata]
        return np.array(datetimes).reshape(tdata.shape)

    @property
    def is_lonlat_dim(self):
        """
        Returns:
        --------
        is_lonlat_dim : bool
            True if lon,lat are dimensions
        """
        return (self.lonlat_names[0] in self.dimensions)

    def get_xy_dims_from_lonlat(self, lon, lat, accuracy=1e3):
        """
        Get the x,y vectors for the dimensions if they are not provided in the netcdf file
        Assumes a regular grid in the input projection

        Parameters:
        -----------
        lon : np.ndarray
            2d longitude array, units = degrees_east
        lat : np.ndarray
            2d latitude array, units = degrees_north
        accuracy : float
            desired accuracy in m - we round to this accuracy so
            that x and y are regularly spaced

        Returns:
        --------
        x : np.ndarray
            x coordinate vector, units = m
        y : np.ndarray
            y coordinate vector, units = m
        """
        assert(not self.is_lonlat_dim)
        x = self.projection.pyproj(lon[0,:], lat[0,:])[0]
        y = self.projection.pyproj(lon[:,0], lat[:,0])[1]
        return [np.round(v/accuracy)*accuracy for v in [x, y]]

    @property
    def datetimes(self):
        """
        Returns:
        --------
        datetimes : list(datetime.datetime)
            all the time values converted to datetime objects
        """
        if self.time_name is None:
            return []
        return list(self.convert_time_data(self.variables[self.time_name][:]))

    def get_nearest_date(self, pivot):
        """ Get date from the Dataset closest to the input date
        
        Parameters
        ----------
        pivot : datetime.datetime
            searching date

        Returns
        -------
        dto : datetime.datetime
            value nearest date
        time_index : int
            index of the nearest date

        """
        dto = min(self.datetimes, key=lambda x: abs(x - pivot))
        time_index = self.datetimes.index(dto)
        return dto, time_index


class GeoDatasetWrite(GeoDatasetBase):
    """ Wrapper for netCDF4.Dataset for common ouput tasks """

    def __init__(self, *args, **kwargs):
        """
        Initialise the object and add some default parameters which can be overridden by child classes.
        Default parameters correspond to neXtSIM Moorings files.

        Parameters:
        -----------
        args and kwargs for netCDF4.Dataset

        Sets:
        -----
        projection : ProjectionInfo
        projection_names : tuple(str)
            (grid_mapping, grid_mapping_name)
            - grid_mapping is the name of the projection variable
            - grid_mapping_name is the name of the projection variable
        spatial_dim_names : tuple(str)
            names of spatial dimensions
        lonlat_names : tuple(str)
            names of lon,lat variables
        time_name : str
            name of time variable
        """
        super().__init__(*args, **kwargs)
        self.projection_names = ('Polar_Stereographic_Grid', 'polar_stereographic')
        self.spatial_dim_names = ('x', 'y')
        self.time_name = 'time'
        self.lonlat_names = ('longitude', 'latitude')
        self.projection = ProjectionInfo()
    
    def set_projection_variable(self):
        """
        set projection variable.

        See conventions in:
        http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html

        Check netcdf files at:
        http://cfconventions.org/compliance-checker.html
        """
        gm, gmn = self.projection_names
        pvar = self.createVariable(gm, 'i1')
        pvar.setncatts(self.projection.ncattrs(gmn))
        pvar.setncatts(dict(
            proj4="+proj=stere +lat_0=90 +lat_ts=90 +lon_0=-45 +x_0=0 +y_0=0 +R=6378273 +ellps=sphere +units=m +no_defs"))

    def set_time_variables_dimensions(self, time_data, time_atts, time_bnds_data):
        """
        set the temporal dimensions (time, nv)
        and variables (time, time_bnds)

        Parameters:
        -----------
        time_data : np.array
            data for time variable
        time_atts : dict
            netcdf attributes for time variable
        time_bnds_data : np.array
            data for time_bnds variable
        time_bnds_atts : dict
            netcdf attributes for time_bnds variable
        """
        # dimensions
        self.createDimension('time', None)#time should be unlimited
        self.createDimension('nv', 2)
        # time should have units and a calendar attribute
        ncatts = dict(**time_atts)
        ncatts['calendar'] = time_atts.get('calendar', 'standard')
        units = time_atts['units']
        # time var
        tvar = self.createVariable('time', 'f8', ('time',), zlib=True)
        tvar.setncatts(ncatts)
        tvar[:] = time_data
        # time_bnds var - just needs units
        tbvar = self.createVariable('time_bnds', 'f8', ('time', 'nv'), zlib=True)
        tbvar.setncattr('units', units)
        tbvar[:] = time_bnds_data

    def set_xy_dims(self, x, y):
        """
        set the x,y dimensions and variables

        Parameters:
        -----------
        x : np.ndarray
            vector of x coordinate (units = m)
        y : np.ndarray
            vector of y coordinate (units = m)
        """
        for dim_name, dim_vec in zip(['y', 'x'], [y, x]):
            dst_dim = self.createDimension(dim_name, len(dim_vec))
            dst_var = self.createVariable(dim_name, 'f8', (dim_name,), zlib=True)
            dst_var.setncattr('standard_name', 'projection_%s_coordinate' %dim_name)
            dst_var.setncattr('units', 'm')
            dst_var.setncattr('axis', dim_name.upper())
            dst_var[:] = dim_vec

    def set_lonlat(self, lon, lat):
        """
        set the lon, lat variables

        Parameters:
        -----------
        lon : np.ndarray
            array of longitudes (units = degrees_east)
        lat : np.ndarray
            array of latitudes (units = degrees_north)
        """
        data_units = [
                ('longitude', lon, 'degrees_east'),
                ('latitude',  lat, 'degrees_north'),
                ]
        dims = tuple(self.spatial_dim_names[::-1])
        for vname, data, units in data_units:
            dst_var = self.createVariable(vname, 'f8', dims, zlib=True)
            dst_var.setncattr('standard_name', vname)
            dst_var.setncattr('long_name', vname)
            dst_var.setncattr('units', units)
            dst_var[:] = data

    def set_variable(self, vname, data, dims, atts, dtype='f4'):
        """
        set variable data and attributes

        Parameters:
        -----------
        vname : str
            name of new variable
        data : numpy.ndarray
            data to set in variable
        dims : list(str)
            list of dimension names for the variable
        atts : dict
            netcdf attributes to set
        dtype : str
            netcdf data type for new variable (eg 'f4' or 'f8')
        """
        self.logger.debug('Creating variable %s' %vname)
        type_converter = dict(f4=np.float32, f8=np.double)[dtype]
        ncatts = {k:v for k,v in atts.items() if k != '_FillValue'}
        kw = dict(zlib=True)# use compression
        if '_FillValue' in atts:
            # needs to be a keyword for createVariable and of right data type
            kw['fill_value'] = type_converter(atts['_FillValue'])
        if 'missing_value' in atts:
            # needs to be of right data type
            ncatts['missing_value'] = type_converter(atts['missing_value'])
        dst_var = self.createVariable(vname, dtype, dims, **kw)
        ncatts['grid_mapping'] = self.projection_names[0]
        dst_var.setncatts(ncatts)
        dst_var[:] = data


class GeoDatasetRead(GeoDatasetBase):
    """ Wrapper for netCDF4.Dataset for common input tasks """

    def __init__(self, *args, **kwargs):
        """
        Initialise the object and add some default parameters which can be overridden by child classes.
        Default parameters correspond to neXtSIM Moorings files.

        Parameters:
        -----------
        args and kwargs for netCDF4.Dataset

        Sets:
        -----
        projection : ProjectionInfo
        projection_names : tuple(str)
            (grid_mapping, grid_mapping_name)
            - grid_mapping is the name of the projection variable
            - grid_mapping_name is the name of the projection variable
        spatial_dim_names : tuple(str)
            names of spatial dimensions
        lonlat_names : tuple(str)
            names of lon,lat variables
        time_name : str
            name of time variable
        """
        super().__init__(*args, **kwargs)
        # TODO:
        # read these from input file or define in inhertited classes 
        self.projection_names = ('Polar_Stereographic_Grid', 'polar_stereographic')
        self.spatial_dim_names = ('x', 'y')
        self.time_name = 'time'
        self.projection = ProjectionInfo()
        self.lonlat_names = self._get_lonlat_names()
        self.variable_names = self._get_variable_names()
        self.area_definition = self._get_area_definition()

    def _get_lonlat_names(self):
        """ Get names of latitude longitude following CF and ACDD standards """
        lon_standard_name = 'longitude'
        lat_standard_name = 'latitude'
        lon_var_name = lat_var_name = None
        for var_name, var_val in self.variables.items():
            if 'standard_name' in var_val.ncattrs():
                if var_val.standard_name == lon_standard_name:
                    lon_var_name = var_name
                if var_val.standard_name == lat_standard_name:
                    lat_var_name = var_name
            if lon_var_name and lat_var_name:
                return lon_var_name, lat_var_name
        raise InvalidDatasetError

    def _get_variable_names(self):
        """ Find valid names of variables excluding names of dimensions, projections, etc
        
        Returns
        -------
        var_names : list of str
            names of valid variables

        """
        bad_names = list(self.dimensions.keys())
        var_names = list(self.variables.keys())
        bad_names.extend(list(self.projection_names))
        bad_names += ['time_bnds']
        for bad_name in bad_names:
            if bad_name in var_names:
                var_names.remove(bad_name)
        return var_names
    
    def _get_area_definition(self):
        try:
            area, extra = load_cf_area(self.filename)
        except [MissingDimensionsError, CRSError, KeyError, ValueError] as e:
            raise InvalidDatasetError
        
    def get_variable_array(self, var_name, time_index=0):
        ds_var = self[var_name]
        array = ds_var[:]
        if 'time' in ds_var.dimensions:
            time_axis = ds_var.dimensions.index('time')
            array = array.take(indices=time_index, axis=time_axis)
        return array

    def get_lonlat_arrays(self):
        # if lon and lat are arrays
        return [self.get_variable_array(name) for name in self.lonlat_names]
