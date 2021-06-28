
class Interpolator:

    def __init__(self, source_area, target_area, method, **kwargs):
        self.source_area = source_area
        self.target_area = target_area
        self.method = method
        self.resampler = self.method(self.source_area, self.target_area, **kwargs)
        self.__dict__.update(kwargs)
