import ast
import pytest
from detection_rules.api_specific.dataframe_conversion_api_misused import (
    DataFrameConversionAPIMisused,
)


@pytest.fixture
def detector():
    """
    Fixture to initialize the DataFrameConversionAPIMisused instance.
    """
    return DataFrameConversionAPIMisused()


def test_detect_no_smell(detector):
    """
    Test the detect method when no misuse of the `values` attribute is present.
    """
    code = (
        "import pandas as pd\n"
        "def no_smell():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    value = df.loc[0, 'a']\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(detector):
    """
    Test the detect method when a single
    misuse of the `values` attribute is present.
    """
    code = (
        "import pandas as pd\n"
        "def convert_dataframe():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    value = df.values\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["line"] == 4  # Line of the smell
    assert (
        "Misuse of the 'values' attributedetected in variable"
        in result[0]["additional_info"]
    )


def test_detect_without_pandas_library(detector):
    """
    Test the detect method when the pandas library is not imported.
    """
    code = (
        "def no_pandas():\n"
        "    df = {'a': [1, 2, 3]}\n"
        "    value = df['a'][0]\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No pandas alias
        "dataframe_variables": [],
    }

    result = detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(detector):
    """
    Test the detect method when multiple
    misuses of the `values` attribute are present.
    """
    code = (
        "import pandas as pd\n"
        "def api_misused():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    value1 = df.values\n"
        "    value2 = df.values\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 4  # Line of the first smell
    assert result[1]["line"] == 5  # Line of the second smell
    assert (
        "Misuse of the 'values' attributedetected in variable"
        in result[0]["additional_info"]
    )
    assert (
        "Misuse of the 'values' attributedetected in variable"
        in result[1]["additional_info"]
    )
