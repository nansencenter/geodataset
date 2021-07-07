import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geodataset",
    version="0.0.1",
    author="Arash Azamifard",
    author_email="arash.azamifard@nersc.no",
    description="regridding tool for Geospatial data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nansencenter/geodataset",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["numpy",
                      "scipy",
                      "matplotlib",
                      "notebook",
                      "pyproj",
                      "cython",
                      "shapely",
                      "netcdftime",
                      "cartopy",
                      "satpy"],
    python_requires='>=3.7'
)
