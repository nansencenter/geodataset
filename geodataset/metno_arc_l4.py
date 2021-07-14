from os.path import basename

from geodataset.area_definitions import METNOARCsvalbardAreaDefinition
from geodataset.geo_dataset import  GeoDataset
from geodataset.utils import BadAreaDefinition


class METNOARCsvalbard(GeoDataset):
    def _load_area(self):
        if not basename(self.file_path).startswith("ice_conc_svalbard_"):
            raise BadAreaDefinition
        try:
            temporary_AreaDefinition_object = METNOARCsvalbardAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = temporary_AreaDefinition_object.get_area()
        del temporary_AreaDefinition_object
