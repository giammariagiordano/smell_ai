import ast
import pytest
from detection_rules.api_specific.gradients_not_cleared_before_backward_propagation import (  # noqa: E501
    GradientsNotClearedSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the GradientsNotClearedSmell instance.
    """
    return GradientsNotClearedSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when gradients
    are cleared before backward propagation.
    """
    code = (
        "import torch\n"
        "def train():\n"
        "    optimizer = torch.optim.SGD([], lr=0.01)\n"
        "    for epoch in range(10):\n"
        "        optimizer.zero_grad()\n"
        "        loss = torch.tensor(0.0, requires_grad=True)\n"
        "        loss.backward()\n"
    )
    tree = ast.parse(code)

    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {
            "optimizer": ast.Assign(
                targets=[ast.Name(id="optimizer", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="torch", ctx=ast.Load()),
                            attr="optim",
                            ctx=ast.Load(),
                        ),
                        attr="SGD",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[
                        ast.keyword(arg="lr", value=ast.Constant(value=0.01))
                    ],
                ),
            ),
            "loss": ast.Assign(
                targets=[ast.Name(id="loss", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="tensor",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=0.0)],
                    keywords=[
                        ast.keyword(
                            arg="requires_grad", value=ast.Constant(value=True)
                        )
                    ],
                ),
            ),
        },
        "lines": {
            4: "for epoch in range(10):",
            5: "optimizer.zero_grad()",
            6: "loss = torch.tensor(0.0, requires_grad=True)",
            7: "loss.backward()",
        },
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when gradients
    are not cleared before backward propagation.
    """
    code = (
        "import torch\n"
        "def train():\n"
        "    optimizer = torch.optim.SGD([], lr=0.01)\n"
        "    for epoch in range(10):\n"
        "        loss = torch.tensor(0.0, requires_grad=True)\n"
        "        loss.backward()\n"
    )
    tree = ast.parse(code)

    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {
            "optimizer": ast.Assign(
                targets=[ast.Name(id="optimizer", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="torch", ctx=ast.Load()),
                            attr="optim",
                            ctx=ast.Load(),
                        ),
                        attr="SGD",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[
                        ast.keyword(arg="lr", value=ast.Constant(value=0.01))
                    ],
                ),
            ),
            "loss": ast.Assign(
                targets=[ast.Name(id="loss", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="tensor",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=0.0)],
                    keywords=[
                        ast.keyword(
                            arg="requires_grad", value=ast.Constant(value=True)
                        )
                    ],
                ),
            ),
        },
        "lines": {
            4: "for epoch in range(10):",
            5: "loss = torch.tensor(0.0, requires_grad=True)",
            6: "loss.backward()",
        },
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert (
        "`zero_grad()` not called before `backward()`"
        in result[0]["additional_info"]
    )
    assert result[0]["line"] == 6  # Line where the smell occurs


def test_detect_without_torch_library(smell_detector):
    """
    Test the detect method when the Torch library is not imported.
    """
    code = (
        "def train():\n"
        "    optimizer = None\n"
        "    for epoch in range(10):\n"
        "        loss = 0.0\n"
        "        pass\n"
    )
    tree = ast.parse(code)

    extracted_data = {
        "libraries": {},  # No Torch alias
        "variables": {},
        "lines": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_multiple_smells(smell_detector):
    """
    Test the detect method when multiple gradient
    clearing issues are present.
    """
    code = (
        "import torch\n"
        "def train():\n"
        "    optimizer = torch.optim.SGD([], lr=0.01)\n"
        "    for epoch in range(10):\n"
        "        loss = torch.tensor(0.0, requires_grad=True)\n"
        "        loss.backward()\n"
        "    for step in range(5):\n"
        "        another_loss = torch.tensor(0.1, requires_grad=True)\n"
        "        another_loss.backward()\n"
    )
    tree = ast.parse(code)

    extracted_data = {
        "libraries": {"torch": "torch"},
        "variables": {
            "optimizer": ast.Assign(
                targets=[ast.Name(id="optimizer", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="torch", ctx=ast.Load()),
                            attr="optim",
                            ctx=ast.Load(),
                        ),
                        attr="SGD",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[
                        ast.keyword(arg="lr", value=ast.Constant(value=0.01))
                    ],
                ),
            ),
            "loss": ast.Assign(
                targets=[ast.Name(id="loss", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="tensor",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=0.0)],
                    keywords=[
                        ast.keyword(
                            arg="requires_grad", value=ast.Constant(value=True)
                        )
                    ],
                ),
            ),
            "another_loss": ast.Assign(
                targets=[ast.Name(id="another_loss", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="tensor",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=0.1)],
                    keywords=[
                        ast.keyword(
                            arg="requires_grad", value=ast.Constant(value=True)
                        )
                    ],
                ),
            ),
        },
        "lines": {
            4: "for epoch in range(10):",
            5: "loss = torch.tensor(0.0, requires_grad=True)",
            6: "loss.backward()",
            7: "for step in range(5):",
            8: "another_loss = torch.tensor(0.1, requires_grad=True)",
            9: "another_loss.backward()",
        },
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 2  # Two smells should be detected
    assert result[0]["line"] == 6  # Line of the first smell
    assert result[1]["line"] == 9  # Line of the second smell
