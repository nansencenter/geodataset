import importlib
from json import load

import numpy as np
from pyresample import bilinear

from formats.geodataset import GeoDataset
from interpolators.gridgrid import GridGridInterpolator


def main():
    with open("/workspaces/Regridder/regridder/classes.json", 'r') as classes_file:
        dict_from_json = load(classes_file)
    target_file_address = '/workspaces/Regridder/regridder/data/ice_conc_nh_polstere-100_multi_202106131200.nc'
    dict_from_json.pop(target_file_address)
    target = GeoDataset(target_file_address)
    for address_of_file, value_ in dict_from_json.items():
        if value_ != []:
            package_dot_module_dot_classname = value_[0]# the first one among the matched classes is used
            class_name  = package_dot_module_dot_classname.rsplit(".", 1)[1]
            package_and_module_name = package_dot_module_dot_classname.rsplit(".", 1)[0]
            source_module = importlib.import_module(package_and_module_name)
            # source (which is the address_of_file) is instatiated with the line below
            source_ = source_module.__dict__[class_name](address_of_file)
            ggi = GridGridInterpolator(
                                source_.area, target.area, method=bilinear.NumpyBilinearResampler,
                                radius_of_influence=15000
                                      )
            cons_from_nc_file = np.ones(source_.area.shape)
            #cons_from_nc_file = source_._get_var('sea_ice_concentration', time_index=0).values
            source_._set_time_info()
            resampled_data_cons = ggi(cons_from_nc_file)



if __name__ == "__main__":
    main()
