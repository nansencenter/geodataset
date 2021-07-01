import glob
import importlib
import inspect
import pkgutil
import sys
from json import dump
from os.path import dirname, join

import formats


def main():
    search_folder = "/workspaces/Regridder/regridder/data"
    search_path = join(search_folder, "**/*.nc")
    list_of_netcdf_files = glob.glob(search_path, recursive=True)
    matched_class = {}
    formats_package_path = dirname(formats.__file__)
    for netcdf_file_address in list_of_netcdf_files:
        matched_class[netcdf_file_address] = list()
        for _, module_name, _ in pkgutil.iter_modules([formats_package_path]):
        # for all the modules in the 'formats' package
            module_full_path = f'formats.{module_name}'
            importlib.import_module(module_full_path)
            for member_name, member in inspect.getmembers(sys.modules[module_full_path]):
            # for all classes (in general term 'member') inside the module
                if inspect.isclass(member) and member.__module__.startswith(module_full_path):
                    try:# try to instatiate with the class in order to test whether it is working or not
                        instantiated_object = member(netcdf_file_address)
                    except AttributeError:
                        # in the case of intermediate class we have AttributeError which should not
                        # do anything in this loop because this loop only concerns the child classes
                        if member_name == 'NoneStandardGeoDataset':
                            continue
                        else:
                            raise
                    except (ValueError, IndexError):
                        # ValueError is for inability of GeoDataset class (default behaviour class
                        # by pyresample) to read the file. This happens for the files that pyresample
                        # can not read them.
                        # IndexError is for lack of proper class(incorrect class) to read the netcdf file
                        continue
                    except OSError:
                        # IndexError is for "badly copied" or "corrupted" netcdf file(s)
                        print("><><"+netcdf_file_address+" is a broken file!")
                        continue
                    else:
                        # If the file can be read by pyresample, there is no need to do anything more.
                        # Otherwise add the name of class that can read the netcdf file.
                        if ('formats.geodataset.GeoDataset' not in matched_class[netcdf_file_address]
                            and instantiated_object.area is not None):
                            matched_class[netcdf_file_address].append(member.__module__ +'.'+ member_name)

    for key, value in matched_class.items():
        if len(value)>1:
            print("WARNING: "+str(key)+" has more than one matched class")
        if len(value)==0:
            print("WARNING: "+str(key)+" has no matched class")

    with open(join(dirname(search_folder), "classes.json"), 'w') as outfile:
        dump(matched_class, outfile, indent=4)



if __name__ == "__main__":
    main()
