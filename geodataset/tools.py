from geodataset.customized_geo_dataset import (ASRFINAL, AMSR2IceConc,
                                               Dist2Coast, ETOPOArctic,
                                               METNOARCsvalbard, Moorings,
                                               Topaz4Arc)
from geodataset.geo_dataset import GeoDataset
from geodataset.utils import BadAreaDefinition


def open_netcdf(file_address):
    classes = [GeoDataset, Moorings, Topaz4Arc, AMSR2IceConc, ASRFINAL, METNOARCsvalbard, ETOPOArctic, Dist2Coast]
    for class_ in classes:
        try:
            obj = class_(file_address)
        except BadAreaDefinition:
            continue # skip to the next class in the list
        return obj # return object when try was successful

    # raise error when none of classes suited
    raise ValueError("Can not find proper geodataset-based class for this file: " + file_address)
