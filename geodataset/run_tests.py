import unittest

from tests.test_utils import UtilsTestCases
from tests.test_geo_dataset import GeodatasetTestCases
from tests.test_variable import VariableTestCases
from tests.test_tools import ToolsTestCases
from tests.test_resampling import ResamplingTestCases
from tests.test_nextsim_moorings import MooringsTestCases
from tests.test_interpolation import InterpolationTestCases
from tests.test_area_definitions import (CustomAreaDefinitionTestCases,
                                    ValueBasedMooringsAreaDefinitionTestCases,
                                    ValueBasedAreaDefinitionTestCases)

if __name__ == '__main__':
    unittest.main(failfast=True)
