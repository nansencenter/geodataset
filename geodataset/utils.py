import inspect
import os
import logging

def clean_path(path):
    """
    removes trailing '/' or '//' to make os.path.split work as expected
    Parameters:
    -----------
    path : str
    Returns:
    --------
    clean_path : str
        eg a//b/c/ -> a/b/c
    """
    s = path
    while 2*os.sep in s:
        s = s.replace(2*os.sep, os.sep)
    while s.endswith(os.sep):
        s = s[:-1]
    return s

def split_path(path):
    """
    safer version of os.path.split
    Parameters:
    -----------
    path : str
    Returns:
    --------
    split_path : list(str)
        eg a/b/c -> [a/b, c]
        eg a//b/c/ -> [a/b, c] (fails with os.path.split)
    """
    return os.path.split(clean_path(path))

def get_module_name(cls):
    """
    get name of module that class belongs to. Starts with file containing the class,
    then searches parent directories until it finds '__init__.py'.
    If it is not found then the file's basename is returned (without the .py extension).
    Parameter:
    ----------
    cls: type
        class type eg object.__class__
    Returns:
    --------
    module_name : str
    """
    path = os.path.abspath(inspect.getfile(cls))
    p1, basename = split_path(os.path.splitext(path)[0])
    p2 = basename
    stop = False
    while p1 != '/':
        p1, p2_ = split_path(p1)
        p2 = f'{p2_}.{p2}'
        if stop:
            return p2
        stop = '__init__.py' in os.listdir(p1) #p1 is the root module - stop after one more iteration
    return 

def get_logger(cls):
    """
    get logger which takes its name from the class it will be go into
    Parameters:
    -----------
    cls : type
        class type eg object.__class__
    Returns:
    --------
    logger : logging.Logger
        logger with name from cls
        and with NullHandler added
    """
    logger = logging.getLogger(get_module_name(cls))
    logger.addHandler(logging.NullHandler())
