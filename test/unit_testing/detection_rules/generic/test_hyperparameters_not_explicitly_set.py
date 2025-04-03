import ast
import pytest
from detection_rules.generic.hyperparameters_not_explicitly_set import (
    HyperparametersNotExplicitlySetSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the HyperparametersNotExplicitlySetSmell instance.
    """
    return HyperparametersNotExplicitlySetSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when all hyperparameters are explicitly set.
    """
    code = (
        "import sklearn.ensemble as se\n"
        "def main():\n"
        "    model = se.RandomForestClassifier"
        "(n_estimators=100, max_depth=5)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"sklearn": "se"},
        "model_methods": ["RandomForestClassifier()"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when hyperparameters are not explicitly set.
    """
    code = (
        "import sklearn.ensemble as se\n"
        "def main():\n"
        "    model = se.RandomForestClassifier()\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"sklearn": "se"},
        "model_methods": ["RandomForestClassifier()"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "hyperparameters_not_explicitly_set"
    assert "Hyperparameters not explicitly set" in result[0]["additional_info"]
    assert result[0]["line"] == 3  # Line where the smell occurs


def test_detect_without_library(smell_detector):
    """
    Test the detect method when the library is not imported.
    """
    code = (
        "\n"
        "\n"
        "def main():\n"
        "\n"
        "    model1 = RandomForestClassifier()\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},
        "model_methods": ["RandomForestClassifier()"],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple
    models are defined without hyperparameters.
    """
    code = (
        "import sklearn.ensemble as se\n"
        "def main():\n"
        "    model1 = se.RandomForestClassifier()\n"
        "    model2 = se.GradientBoostingClassifier()\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"sklearn": "se"},
        "model_methods": [
            "RandomForestClassifier()",
            "GradientBoostingClassifier()",
        ],
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 3  # Line of the first smell
    assert result[1]["line"] == 4  # Line of the second smell
