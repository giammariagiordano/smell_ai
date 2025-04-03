import ast
import pytest
from detection_rules.generic.unnecessary_iteration import (
    UnnecessaryIterationSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the UnnecessaryIterationSmell instance.
    """
    return UnnecessaryIterationSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no unnecessary iteration is present.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    df['b'] = df['a'] * 2\n"  # Proper vectorized operation
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_iterrows(smell_detector):
    """
    Test the detect method when `iterrows` is used in a loop.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    for index, row in df.iterrows():\n"
        "        print(row['a'])\n"  # Inefficient iteration
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "unnecessary_iteration"
    assert "Inefficient iteration" in result[0]["additional_info"]
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_with_apply_in_loop(smell_detector):
    """
    Test the detect method when `apply` is used inside a loop.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    while True:\n"
        "        df['b'] = df['a'].apply(lambda x: x + 1)\n"
        # Inefficient operation
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "unnecessary_iteration"
    assert "Inefficient operation" in result[0]["additional_info"]
    assert result[0]["line"] == 5  # Line where the smell occurs


def test_detect_without_pandas_library(smell_detector):
    """
    Test the detect method when the Pandas library is not imported.
    """
    code = (
        "data = {'a': [1, 2, 3]}\n"
        "for key, value in data.items():\n"
        "    print(value)\n"
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
    Test the detect method when multiple inefficient iterations are present.
    """
    code = (
        "import pandas as pd\n"
        "def main():\n"
        "    df = pd.DataFrame({'a': [1, 2, 3]})\n"
        "    for index, row in df.iterrows():\n"
        "        print(row['a'])\n"
        "    while True:\n"
        "        df['b'] = df['a'].apply(lambda x: x + 1)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": ["df"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 4  # Line of the first smell
    assert result[1]["line"] == 7  # Line of the second smell
