import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geodataset",
    version="0.1.0",
    author=["Anton Korosov", "Timothy Williams"],
    author_email="Anton.Korosov@nersc.no",
    description="Extension of netDCF4.Dataset for geospatial data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nansencenter/geodataset",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        "cartopy",
        "netCDF4",
        "netcdftime",
        "numpy",
        "pyproj",
        "pyresample",
        "xarray"],
    python_requires='>=3.8'
)
