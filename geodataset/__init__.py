"""
This module provides classes and scripts for the pynextsimf package
"""

import logging.config
import os
import sys
import yaml

"""
Scripts etc get logger with "from pynextsimf import get_logger",
thereby running this file and configuring the logger. Otherwise
unless there is an explicit import of something from pynextsimf,
the logging is not configured
"""
from geodataset.utils import get_logger

DEFAULT_LOGGING_CONF_FILE = os.path.join(os.path.dirname(__file__), 'logging.yml')
LOGGING_CONF_FILE = os.getenv('PYNEXTSIMF_LOG_CONF_PATH', DEFAULT_LOGGING_CONF_FILE)

try:
    with open(LOGGING_CONF_FILE, 'rb') as stream:
        logging_configuration = yaml.safe_load(stream)  # pylint: disable=invalid-name
except FileNotFoundError:
    print(f"'{LOGGING_CONF_FILE}' does not exist, logging can't be configured.", file=sys.stderr)
    logging_configuration = None  # pylint: disable=invalid-name

if logging_configuration:
    logging.config.dictConfig(logging_configuration)
    logging.captureWarnings(True)
