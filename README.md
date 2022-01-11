# geodataset

Extension of netCDF4.Dataset for geospatial data.

# Installation

Install requirements with conda:

`conda env create -f environment.yml`

Activate the environment:

`conda activate geodataset`

Install geodataset using pip:

`pip install geodataset`

# Usage

Open netCDF file for input and access geo- metadata

```python
from geodataset.tools import open_netcdf

n = open_netcdf('netcdf_file.nc')

print(n.projection)

print(n.get_bbox())

print(n.get_lonlat_arrays())
```