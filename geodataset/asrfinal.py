from os.path import basename

from geodataset.area_definitions import ASRFINALAreaDefinition
from geodataset.geo_dataset import  GeoDataset
from geodataset.utils import BadAreaDefinition


class ASRFINAL(GeoDataset):
    def _load_area(self):
        if not basename(self.file_path).startswith("asr30km"):
            raise BadAreaDefinition
        try:
            temporary_AreaDefinition_object = ASRFINALAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = temporary_AreaDefinition_object.get_area()
        del temporary_AreaDefinition_object
