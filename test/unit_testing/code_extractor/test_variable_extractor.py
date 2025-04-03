import pytest
from unittest.mock import MagicMock
import ast
from code_extractor.variable_extractor import VariableExtractor


@pytest.fixture
def extractor():
    """Fixture to create and return a VariableExtractor instance."""
    return VariableExtractor()


def test_extract_variable_definitions(mocker, extractor):
    """Test extracting variable definitions from a function node."""

    # Create mock AST nodes for assignments
    mock_assign_1 = MagicMock(spec=ast.Assign)
    mock_assign_2 = MagicMock(spec=ast.Assign)

    mock_name_1 = MagicMock(spec=ast.Name)
    mock_name_1.id = "x"  # Variable 'x' is being assigned
    mock_name_2 = MagicMock(spec=ast.Name)
    mock_name_2.id = "y"  # Variable 'y' is being assigned

    # Assign these mock Name nodes to the Assign nodes
    mock_assign_1.targets = [mock_name_1]
    mock_assign_2.targets = [mock_name_2]

    # Mock ast.walk to return these assignments
    mock_walk = mocker.patch(
        "ast.walk", return_value=[mock_assign_1, mock_assign_2]
    )

    # Simulate the AST of a function node
    fun_node = MagicMock(spec=ast.FunctionDef)

    # Call the method being tested
    definitions = extractor.extract_variable_definitions(fun_node)

    # Expected result: the dictionary should contain 'x' and 'y'
    expected = {
        "x": mock_assign_1,
        "y": mock_assign_2,
    }

    assert definitions == expected
    mock_walk.assert_called_once_with(fun_node)


def test_track_variable_usage(mocker, extractor):
    """Test tracking variable usage in a function node."""

    # Create mock AST nodes for variable usages
    mock_name_1 = MagicMock(spec=ast.Name)
    mock_name_1.id = "x"  # Variable 'x' is used

    mock_name_2 = MagicMock(spec=ast.Name)
    mock_name_2.id = "y"  # Variable 'y' is used

    # Mock ast.walk to return these Name nodes
    mock_walk = mocker.patch(
        "ast.walk", return_value=[mock_name_1, mock_name_2]
    )

    # Simulate the AST of a function node
    fun_node = MagicMock(spec=ast.FunctionDef)

    # Call the method being tested
    usage = extractor.track_variable_usage(fun_node)

    # Expected result: the dictionary should contain 'x' and 'y'
    expected = {
        "x": [mock_name_1],
        "y": [mock_name_2],
    }

    assert usage == expected
    mock_walk.assert_called_once_with(fun_node)


def test_empty_function(mocker, extractor):
    """Test case for an empty function with no variable definitions
    or usage."""

    # Mock ast.walk to return an empty list (no nodes)
    mock_walk = mocker.patch("ast.walk", return_value=[])

    # Simulate an empty AST function node
    fun_node = MagicMock(spec=ast.FunctionDef)

    # Call the methods being tested
    definitions = extractor.extract_variable_definitions(fun_node)
    usage = extractor.track_variable_usage(fun_node)

    # Both should return empty dictionaries as there are no variable
    # definitions or usages
    assert definitions == {}
    assert usage == {}

    # Expect ast.walk to be called twice (once for each method)
    mock_walk.assert_any_call(fun_node)
    assert mock_walk.call_count == 2  # Expect two calls in total
