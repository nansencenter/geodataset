from .interpolator import Interpolator


class GridGridInterpolator(Interpolator): #(pyresample)

    def __call__(self, variable):
        return self.resampler.resample(variable)
