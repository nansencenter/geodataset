from os.path import basename

from geodataset.area_definitions import (AMSR2IceConcAreaDefinition,
                                         ASRFINALAreaDefinition,
                                         METNOARCsvalbardAreaDefinition,
                                         MooringsAreaDefinition,
                                         Topaz4ArcAreaDefinition)
from geodataset.geo_dataset import GeoDataset
from geodataset.utils import BadAreaDefinition


class CustomizedGeoDataset(GeoDataset):

    def _load_area(self):
        """for CustomizedGeoDataset area is obtained with the help of 'CustomizedAreaDefinition' of
        the class."""
        tmp_area_definition = self.CustomizedAreaDefinition(self.file_path)
        self.area = tmp_area_definition.get_area()

    def _check_valid_class(self):
        """check the validity of the class with testing the starting part of filename or with filename
        containing a specific string within."""
        if self.part_of_filename and self.part_of_filename not in basename(self.file_path):
            raise BadAreaDefinition
        if self.start_of_filename and not basename(self.file_path).startswith(self.start_of_filename):
            raise BadAreaDefinition


class AMSR2IceConc(CustomizedGeoDataset):

    CustomizedAreaDefinition = AMSR2IceConcAreaDefinition
    part_of_filename = None
    start_of_filename = "Arc_20"


class ASRFINAL(CustomizedGeoDataset):

    CustomizedAreaDefinition = ASRFINALAreaDefinition
    part_of_filename = None
    start_of_filename = "asr30km"



class METNOARCsvalbard(CustomizedGeoDataset):

    CustomizedAreaDefinition = METNOARCsvalbardAreaDefinition
    part_of_filename = None
    start_of_filename = "ice_conc_svalbard_"


class Moorings(CustomizedGeoDataset):

    CustomizedAreaDefinition = MooringsAreaDefinition
    part_of_filename = None
    start_of_filename = "Moorings"


class Topaz4Arc(CustomizedGeoDataset):

    CustomizedAreaDefinition = Topaz4ArcAreaDefinition
    part_of_filename = "topaz4-ARC"
    start_of_filename = None



class Bathymetry(CustomizedGeoDataset):#incomplete
    CustomizedAreaDefinition =0 #ASRFINALAreaDefinition
    part_of_filename = 0#"topaz4-ARC"
    start_of_filename = 0#None
