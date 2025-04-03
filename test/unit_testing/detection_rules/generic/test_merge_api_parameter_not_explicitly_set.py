import ast
import pytest
from detection_rules.generic.merge_api_parameter_not_explicitly_set import (
    MergeAPIParameterNotExplicitlySetSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the MergeAPIParameterNotExplicitlySetSmell instance.
    """
    return MergeAPIParameterNotExplicitlySetSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when the merge API is
    correctly called with all parameters set.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df1 = pd.DataFrame({'key': [1, 2], 'value': ['a', 'b']})\n"
        "    df2 = pd.DataFrame({'key': [1, 2], 'value': ['x', 'y']})\n"
        "    result = df1.merge(df2, how='inner', on='key',"
        " validate='one_to_one')\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df1", "df2"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_missing_parameters(smell_detector):
    """
    Test the detect method when the merge API is called without parameters.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df1 = pd.DataFrame({'key': [1, 2], 'value': ['a', 'b']})\n"
        "    df2 = pd.DataFrame({'key': [1, 2], 'value': ['x', 'y']})\n"
        "    result = df1.merge(df2)\n"  # Missing parameters
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df1", "df2"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "merge_api_parameter_not_explicitly_set"
    assert "Incomplete parameters in `merge`" in result[0]["additional_info"]
    assert result[0]["line"] == 5  # Line where the smell occurs


def test_detect_incomplete_parameters(smell_detector):
    """
    Test the detect method when the merge API
    is called with incomplete parameters.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df1 = pd.DataFrame({'key': [1, 2], 'value': ['a', 'b']})\n"
        "    df2 = pd.DataFrame({'key': [1, 2], 'value': ['x', 'y']})\n"
        "    result = df1.merge(df2, how='inner')\n"
        # Missing 'on' and 'validate'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df1", "df2"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "merge_api_parameter_not_explicitly_set"
    assert "Incomplete parameters" in result[0]["additional_info"]
    assert result[0]["line"] == 5  # Line where the smell occurs


def test_detect_without_pandas_library(smell_detector):
    """
    Test the detect method when the Pandas library is not imported.
    """
    code = (
        "def main():\n"
        "    df1 = {'key': [1, 2], 'value': ['a', 'b']}\n"
        "    df2 = {'key': [1, 2], 'value': ['x', 'y']}\n"
        "    result = df1.merge(df2)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No Pandas alias
        "dataframe_variables": [],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_multiple_smells(smell_detector):
    """
    Test the detect method when multiple merge
    calls have missing or incomplete parameters.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df1 = pd.DataFrame({'key': [1, 2], 'value': ['a', 'b']})\n"
        "    df2 = pd.DataFrame({'key': [1, 2], 'value': ['x', 'y']})\n"
        "    result1 = df1.merge(df2)\n"  # Missing parameters
        "    result2 = df1.merge(df2, how='inner')\n"
        # Missing 'on' and 'validate'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df1", "df2"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 5  # Line of the first smell
    assert result[1]["line"] == 6  # Line of the second smell
