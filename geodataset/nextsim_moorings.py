from os.path import basename

from geodataset.area_definitions import MooringsAreaDefinition
from geodataset.geodataset import  GeoDataset
from geodataset.utils import BadAreaDefinition


class Moorings(GeoDataset):
    def _load_area(self):
        if not basename(self.file_path).startswith("Moorings"):
            raise BadAreaDefinition
        try:
            temporary_AreaDefinition_object = MooringsAreaDefinition(self.file_path)
        except IndexError:
            raise BadAreaDefinition
        self.area = temporary_AreaDefinition_object.get_area()
        del temporary_AreaDefinition_object
