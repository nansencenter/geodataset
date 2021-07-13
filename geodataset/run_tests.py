import os
import unittest

from tests.test_area_definitions import (
    CustomAreaDefinitionTestCases, ValueBasedAreaDefinitionTestCases,
    ValueBasedMooringsAreaDefinitionTestCases)
from tests.test_geo_dataset import GeodatasetTestCases
from tests.test_interpolation import InterpolationTestCases
from tests.test_nextsim_moorings import MooringsTestCases
from tests.test_resampling import ResamplingTestCases
from tests.test_tools import ToolsTestCases
from tests.test_utils import UtilsTestCases
from tests.test_variable import VariableTestCases

if __name__ == '__main__':
    if 'TEST_DATA_DIR' not in os.environ or os.environ['TEST_DATA_DIR'] =='':
        raise ValueError('TEST_DATA_DIR is not defined or wrongly defined. It should point to example_data.')
    unittest.main(failfast=True)
