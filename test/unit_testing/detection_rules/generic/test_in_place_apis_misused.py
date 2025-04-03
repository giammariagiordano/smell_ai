import ast
import pytest
from detection_rules.generic.in_place_apis_misused import (
    InPlaceAPIsMisusedSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the InPlaceAPIsMisusedSmell instance.
    """
    return InPlaceAPIsMisusedSmell()


def test_detect_no_smell_with_inplace_true(smell_detector):
    """
    Test the detect method when `inplace=True` is explicitly set.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df.drop(columns=['a'], inplace=True)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
        "dataframe_methods": ["drop"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_inplace_false(smell_detector):
    """
    Test the detect method when `inplace=False` is explicitly set.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df.drop(columns=['a'], inplace=False)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
        "dataframe_methods": ["drop"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "in_place_apis_misused"
    assert "Explicitly setting `inplace=False`" in result[0]["additional_info"]
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_no_smell_with_assignment(smell_detector):
    """
    Test the detect method when the result
    of a method call is assigned to a variable.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    new_df = df.drop(columns=['a'])\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
        "dataframe_methods": ["drop"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_no_inplace_and_no_assignment(smell_detector):
    """
    Test the detect method when neither
    `inplace` is set nor the result is assigned.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df.drop(columns=['a'])\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
        "dataframe_methods": ["drop"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "in_place_apis_misused"
    assert (
        "not assigned to a variable, and "
        "the `inplace` parameter is not explicitly set"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_without_pandas_library(smell_detector):
    """
    Test the detect method when the Pandas library is not imported.
    """
    code = (
        "def main():\n"
        "    df = {'a': [1, 2, 3]}\n"
        "    df.drop(columns=['a'], inplace=False)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No Pandas alias
        "dataframe_variables": [],
        "dataframe_methods": [],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected
