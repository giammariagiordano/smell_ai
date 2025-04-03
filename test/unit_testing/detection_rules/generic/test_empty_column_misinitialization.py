import ast
import pytest
from detection_rules.generic.empty_column_misinitialization import (
    EmptyColumnMisinitializationSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the EmptyColumnMisinitializationSmell instance.
    """
    return EmptyColumnMisinitializationSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no column misinitialization is present.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df['new_column'] = pd.NA\n"  # Proper initialization
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_zero_initialization(smell_detector):
    """
    Test the detect method when a column is initialized with zero.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df['new_column'] = 0\n"  # Misinitialization
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "empty_column_misinitialization"
    assert (
        "initialized with a zero or an empty string"
        in result[0]["additional_info"]
    )
    assert "Consider using NaN instead" in result[0]["additional_info"]
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_with_empty_string_initialization(smell_detector):
    """
    Test the detect method when a column is initialized with an empty string.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df['new_column'] = ''\n"  # Misinitialization
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "empty_column_misinitialization"
    assert (
        "initialized with a zero or an empty string"
        in result[0]["additional_info"]
    )
    assert "Consider using NaN instead" in result[0]["additional_info"]
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_without_pandas_library(smell_detector):
    """
    Test the detect method when the Pandas library is not imported.
    """
    code = (
        "def main():\n"
        "    df = {'a': [1, 2, 3]}\n"
        "    df['new_column'] = 0\n"  # This should not be flagged
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No Pandas alias
        "dataframe_variables": [],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple column misinitializations are present.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df['col1'] = 0\n"
        "    df['col2'] = ''\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 4  # Line of the first smell
    assert result[1]["line"] == 5  # Line of the second smell
