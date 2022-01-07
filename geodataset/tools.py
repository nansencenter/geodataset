from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDataset
from geodataset.custom_geodataset import NetcdfArcMFC, CmemsMetIceChart, NerscDeformation, NerscIceType, JaxaAmsr2IceConc

def open_netcdf(file_address):
    classes = [GeoDatasetRead, CmemsMetIceChart, NerscDeformation, NerscIceType, JaxaAmsr2IceConc]
    for class_ in classes:
        try:
            obj = class_(file_address)
        except InvalidDataset:
            continue # skip to the next class in the list
        return obj # return object when try was successful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
