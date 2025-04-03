import ast
import pytest
from detection_rules.api_specific.tensor_array_not_used import (
    TensorArrayNotUsedSmell,
)


@pytest.fixture
def smell_detector():
    """
    Fixture to initialize the TensorArrayNotUsedSmell instance.
    """
    return TensorArrayNotUsedSmell()


def test_detect_no_smell(smell_detector):
    """
    Test the detect method when no misuse of `tf.constant()` is present.
    """
    code = (
        "import tensorflow as tf\n"
        "def main():\n"
        "    x = tf.constant([1, 2, 3])\n"
        "    y = tf.constant([4, 5, 6])\n"
        "    result = tf.concat([x, y], axis=0)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"tensorflow": "tf"},
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_smell(smell_detector):
    """
    Test the detect method when `tf.constant()` is modified inside a loop.
    """
    code = (
        "import tensorflow as tf\n"
        "def main():\n"
        "    x = tf.constant([1, 2, 3])\n"
        "    for i in range(3):\n"
        "        x = tf.concat([x, tf.constant([i])], axis=0)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"tensorflow": "tf"},
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "tensor_array_not_used"
    assert "Using `tf.TensorArray` is better" in result[0]["additional_info"]
    assert result[0]["line"] == 5  # Line where the smell occurs


def test_detect_without_tensorflow_library(smell_detector):
    """
    Test the detect method when the TensorFlow library is not imported.
    """
    code = (
        "def main():\n"
        "    x = [1, 2, 3]\n"
        "    for i in range(3):\n"
        "        x.append(i)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {},  # No TensorFlow alias
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_nested_concat(smell_detector):
    """
    Test the detect method with nested `tf.concat` inside a loop.
    """
    code = (
        "import tensorflow as tf\n"
        "def main():\n"
        "    x = tf.constant([1, 2, 3])\n"
        "    for i in range(3):\n"
        "        x = tf.concat([x, tf.concat([tf.constant([i])], axis=0)]"
        ", axis=0)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"tensorflow": "tf"},
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 1  # One smell should be detected
    assert result[0]["name"] == "tensor_array_not_used"
    assert "Using `tf.TensorArray` is better" in result[0]["additional_info"]
    assert result[0]["line"] == 5  # Line where the smell occurs


def test_detect_constant_not_in_loop(smell_detector):
    """
    Test the detect method when `tf.constant()` is used but not in a loop.
    """
    code = (
        "import tensorflow as tf\n"
        "def main():\n"
        "    x = tf.constant([1, 2, 3])\n"
        "    x = tf.concat([x, tf.constant([4])], axis=0)\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"tensorflow": "tf"},
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected


def test_detect_with_tensor_modified_outside_loop(smell_detector):
    """
    Test the detect method when `tf.constant()` is modified outside a loop.
    """
    code = (
        "import tensorflow as tf\n"
        "def main():\n"
        "    x = tf.constant([1, 2, 3])\n"
        "    x = tf.concat([x, tf.constant([4])], axis=0)\n"
        "    for i in range(3):\n"
        "        y = tf.constant([i])\n"
    )
    tree = ast.parse(code)
    extracted_data = {
        "libraries": {"tensorflow": "tf"},
        "variables": {},
    }

    result = smell_detector.detect(tree, extracted_data)
    assert len(result) == 0  # No smells should be detected
