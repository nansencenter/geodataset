from geodataset.geodataset import GeoDatasetRead
from geodataset.utils import InvalidDatasetError
from geodataset.custom_geodataset import (
    CmemsMetIceChart, 
    Dist2Coast,
    Etopo,
    JaxaAmsr2IceConc, 
    MooringsNextsim,
    NerscDeformation, 
    NerscIceType, 
    OsisafDriftersNextsim,
    SmosIceThickness,
    Topaz4Forecast,
)

custom_read_classes = [
    CmemsMetIceChart, 
    Dist2Coast,
    Etopo,
    JaxaAmsr2IceConc, 
    MooringsNextsim,
    NerscDeformation, 
    NerscIceType,
    OsisafDriftersNextsim,
    SmosIceThickness,
    Topaz4Forecast,
    # always last:
    GeoDatasetRead,
]

def open_netcdf(file_address):

    for class_ in custom_read_classes:
        try:
            obj = class_(file_address)
        except InvalidDatasetError:
            continue # skip to the next class in the list
        return obj # return object when try was successful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
