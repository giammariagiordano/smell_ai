import ast
import pytest
from detection_rules.api_specific.pytorch_call_method_misused import (
    PyTorchCallMethodMisusedSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the PyTorchCallMethodMisusedSmell instance.
    """
    return PyTorchCallMethodMisusedSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no misuse of `forward()` is present.
    """
    code = (
        "import torch\n"
        "class Net(torch.nn.Module):\n"
        "    def forward(self, x):\n"
        "        return x * 2\n"
        "\n"
        "def main():\n"
        "    model = Net()\n"
        "    output = model(torch.tensor([1, 2, 3]))\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {"model": None},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when `forward()`
    is directly called on the model instance.
    """
    code = (
        "import torch\n"
        "class Net(torch.nn.Module):\n"
        "    def forward(self, x):\n"
        "        return x * 2\n"
        "\n"
        "def main():\n"
        "    model = Net()\n"
        "    output = model.forward(torch.tensor([1, 2, 3]))\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {"model": None},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "pytorch_call_method_misused"
    assert "Direct call to" in result[0]["additional_info"]
    assert result[0]["line"] == 8  # Line where the smell occurs


def test_detect_without_torch_library(smell_detector):
    """
    Test the detect method when the PyTorch library is not imported.
    """
    code = (
        "class Net:\n"
        "    def forward(self, x):\n"
        "        return x * 2\n"
        "\n"
        "def main():\n"
        "    model = Net()\n"
        "    output = model.forward([1, 2, 3])\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No PyTorch alias
        "variables": {"model": None},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple `forward()` misuses are present.
    """
    code = (
        "import torch\n"
        "class Net(torch.nn.Module):\n"
        "    def forward(self, x):\n"
        "        return x * 2\n"
        "\n"
        "def main():\n"
        "    model1 = Net()\n"
        "    model2 = Net()\n"
        "    output1 = model1.forward(torch.tensor([1, 2, 3]))\n"
        "    output2 = model2.forward(torch.tensor([4, 5, 6]))\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {"model1": None, "model2": None},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 9  # Line of the first smell
    assert result[1]["line"] == 10  # Line of the second smell


def test_detect_func_value_not_name_or_attribute(smell_detector):
    """
    Test `detect` when `node.func.value` is not `ast.Name`
    or `ast.Attribute`.
    """
    code = (
        "import torch\n"
        "class Net(torch.nn.Module):\n"
        "    def forward(self, x):\n"
        "        return x * 2\n"
        "\n"
        "def main():\n"
        "    model = Net()\n"
        "    output = model.forward(torch.tensor([1, 2, 3]))\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {"model": None},
    }

    # Modify AST node to simulate `func.value`
    #  not being `ast.Name` or `ast.Attribute`
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            node.func.value = ast.Constant(value="invalid")  # Unsupported type

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected
