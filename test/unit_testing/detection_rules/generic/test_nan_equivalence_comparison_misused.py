import ast
import pytest
from detection_rules.generic.nan_equivalence_comparison_misused import (
    NanEquivalenceComparisonMisusedSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the NanEquivalenceComparisonMisusedSmell instance.
    """
    return NanEquivalenceComparisonMisusedSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no NaN misuse is present.
    """
    code = (
        "import numpy as np\n"
        "def main():\n"
        "    value = 5\n"
        "    if np.isnan(value):\n"
        '        print("Value is NaN")\n'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"numpy": "np"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell_equality(smell_detector):
    """
    Test the detect method when NaN is compared using `==`.
    """
    code = (
        "import numpy as np\n"
        "def main():\n"
        "    value = np.nan\n"
        "    if value == np.nan:\n"
        '        print("Value is NaN")\n'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"numpy": "np"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "nan_equivalence_comparison_misused"
    assert (
        "Direct equivalence comparison with NaN"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_with_smell_inequality(smell_detector):
    """
    Test the detect method when NaN is compared using `!=`.
    """
    code = (
        "import numpy as np\n"
        "def main():\n"
        "    value = np.nan\n"
        "    if value != np.nan:\n"
        '        print("Value is not NaN")\n'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"numpy": "np"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "nan_equivalence_comparison_misused"
    assert (
        "Direct equivalence comparison with NaN"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 4  # Line where the smell occurs


def test_detect_without_numpy_library(smell_detector):
    """
    Test the detect method when NumPy library is not imported.
    """
    code = (
        "value = float('nan')\n"
        "if value == float('nan'):\n"
        '    print("Value is NaN")\n'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No NumPy alias
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple NaN misuses are present.
    """
    code = (
        "import numpy as np\n"
        "def main():\n"
        "    value1 = np.nan\n"
        "    value2 = np.nan\n"
        "    if value1 == np.nan:\n"
        '        print("Value1 is NaN")\n'
        "    if value2 != np.nan:\n"
        '        print("Value2 is not NaN")\n'
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"numpy": "np"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 5  # Line of the first smell
    assert result[1]["line"] == 7  # Line of the second smell
