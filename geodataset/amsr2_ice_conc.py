from os.path import basename

from geodataset.area_definitions import AMSR2IceConcAreaDefinition
from geodataset.geo_dataset import  GeoDataset
from geodataset.utils import BadAreaDefinition


class AMSR2IceConc(GeoDataset):
    def _load_area(self):
        if not basename(self.file_path).startswith("Arc_20"):
            raise BadAreaDefinition
        try:
            temporary_AreaDefinition_object = AMSR2IceConcAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = temporary_AreaDefinition_object.get_area()
        del temporary_AreaDefinition_object
