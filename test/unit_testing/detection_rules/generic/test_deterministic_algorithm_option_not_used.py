import ast
import pytest
from detection_rules.generic.deterministic_algorithm_option_not_used import (
    DeterministicAlgorithmOptionSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the DeterministicAlgorithmOptionSmell instance.
    """
    return DeterministicAlgorithmOptionSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no misuse of
    `use_deterministic_algorithms` is present.
    """
    code = (
        "import torch\n"
        "def main():\n"
        "    x = torch.tensor([1, 2, 3])\n"
        "    y = torch.mean(x)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when `use_deterministic_algorithms(True)` is used.
    """
    code = (
        "import torch\n"
        "def main():\n"
        "    torch.use_deterministic_algorithms(True)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "deterministic_algorithm_option_not_used"
    assert (
        "Using `torch.use_deterministic_algorithms(True)`"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 3  # Line where the smell occurs


def test_detect_without_torch_library(smell_detector):
    """
    Test the detect method when the PyTorch library is not imported.
    """
    code = (
        "\n" "def main():\n" "\n" "    th.use_deterministic_algorithms(True)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No PyTorch alias
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_alias(smell_detector):
    """
    Test the detect method when PyTorch is imported with an alias and
    `use_deterministic_algorithms(True)` is used.
    """
    code = (
        "import torch as th\n"
        "def main():\n"
        "    th.use_deterministic_algorithms(True)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "th"},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "deterministic_algorithm_option_not_used"
    assert (
        "Using `torch.use_deterministic_algorithms(True)`"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 3  # Line where the smell occurs
