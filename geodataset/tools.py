from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError
from geodataset.custom_geodataset import NetcdfArcMFC, CmemsMetIceChart, NerscDeformation, NerscIceType, JaxaAmsr2IceConc, Etopo

def open_netcdf(file_address):
    classes = [CmemsMetIceChart, NerscDeformation, NerscIceType, JaxaAmsr2IceConc, Etopo, GeoDatasetRead]
    for class_ in classes:
        try:
            obj = class_(file_address)
        except InvalidDatasetError:
            continue # skip to the next class in the list
        return obj # return object when try was successful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
