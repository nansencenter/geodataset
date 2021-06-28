import pyresample
from pyresample import bilinear

import sys
from formats.geodataset import GeoDataset
from formats.mooring import Mooring
from interpolators.gridgrid import GridGridInterpolator

class Projection:
    pass


def main():
    my_mooring = Mooring('/workspaces/Regridder/regridder/Moorings_2021d179.nc')
    my_GeoDataset = GeoDataset('/workspaces/Regridder/regridder/ice_conc_nh_polstere-100_multi_202106131200.nc')
    ggi = GridGridInterpolator(
                        my_mooring.area, my_GeoDataset.area, method=bilinear.NumpyBilinearResampler,
                        radius_of_influence=15000
                              )
    cons_from_nc_file = my_mooring._get_var('sea_ice_concentration', time_index=0).values
    my_mooring._set_time_info()
    resampled_data_cons = ggi(cons_from_nc_file)



if __name__ == "__main__":
    main()
