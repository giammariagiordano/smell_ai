import ast
import pytest
from detection_rules.api_specific.chain_indexing_smell import (
    ChainIndexingSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the ChainIndexingSmell instance.
    """
    return ChainIndexingSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no chained indexing is present.
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

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when chained indexing is present.
    """
    code = (
        "import pandas as pd\n"
        "def chained_indexing():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    value = df['a'][0]\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "Chain_Indexing"
    assert "Chained indexing detected" in result[0]["additional_info"]
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_without_pandas_library(smell_detector):
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

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple chained indexings are present.
    """
    code = (
        "import pandas as pd\n"
        "def multiple_chained_indexing():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    value1 = df['a'][0]\n"
        "    value2 = df['a'][1]\n"
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
