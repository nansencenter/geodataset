from geodataset import GeoDataset
from nextsim_moorings import Moorings
from utils import BadAreaDefinition

def open_netcdf(file_address):
    classes = [GeoDataset, Moorings]
    for class_ in classes:
        try:
            obj = class_(file_address)
        except BadAreaDefinition:
            continue # skip to the next class in the list
        return obj # return object when try was succesful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
