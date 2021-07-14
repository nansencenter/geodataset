from os.path import basename

from geodataset.area_definitions import Topaz4ArcAreaDefinition
from geodataset.geo_dataset import  GeoDataset
from geodataset.utils import BadAreaDefinition


class Topaz4Arc(GeoDataset):
    def _load_area(self):
        if "topaz4-ARC" not in basename(self.file_path):
            raise BadAreaDefinition
        try:
            temporary_AreaDefinition_object = Topaz4ArcAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = temporary_AreaDefinition_object.get_area()
        del temporary_AreaDefinition_object
