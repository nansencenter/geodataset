import numpy as np
import pyproj
import datetime as dt
from netCDF4 import Dataset
import netcdftime

from geodataset import get_logger
from geodataset.projection_info import ProjectionInfo

class GeoDataset(Dataset):
    """ wrapper for netCDF4.Dataset for common input, output tasks """
    
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
        Dataset.__init__(self, *args, **kwargs)
        self.projection = ProjectionInfo()
        self.projection_names = ('Polar_Stereographic_Grid', 'polar_stereographic')
        self.spatial_dim_names = ('x', 'y')
        self.lonlat_names = ('longitude', 'latitude')
        self.time_name = 'time'
        self.logger = get_logger(self.__class__)

    def __setattr__(self, att, val):
        """ set object attributes (not netcdf attributes)
        This method overrides netCDF4.Dataset.__setattr__, which calls netCDF4.Dataset.setncattr """
        self.__dict__[att] = val

    @property
    def is_lonlat_dim(self):
        """
        Returns:
        --------
        is_lonlat_dim : bool
            True if lon,lat are dimensions
        """
        return (self.lonlat_names[0] in self.dimensions)

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

    # writing
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
        dto        = min(self.datetimes, key=lambda x: abs(x - pivot))
        time_index = self.datetimes.index(dto)
        return dto, time_index


class NetcdfArcMFC(GeoDataset):
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
