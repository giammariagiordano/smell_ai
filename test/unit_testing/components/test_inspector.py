import os
import pytest
import pandas as pd
import ast
from components.inspector import Inspector


@pytest.fixture
def mock_inspector_dependencies(mocker):
    # Use mocker.patch to mock dependencies
    mock_open_file = mocker.patch(
        "builtins.open", new_callable=mocker.mock_open
    )
    mock_ast_parse = mocker.patch("ast.parse")
    MockLibraryExtractor = mocker.patch(
        "components.inspector.LibraryExtractor"
    )
    MockVariableExtractor = mocker.patch(
        "components.inspector.VariableExtractor"
    )
    MockDataFrameExtractor = mocker.patch(
        "components.inspector.DataFrameExtractor"
    )
    MockModelExtractor = mocker.patch("components.inspector.ModelExtractor")
    MockRuleChecker = mocker.patch("components.inspector.RuleChecker")

    yield {
        "mock_open": mock_open_file,
        "mock_ast_parse": mock_ast_parse,
        "MockLibraryExtractor": MockLibraryExtractor,
        "MockVariableExtractor": MockVariableExtractor,
        "MockDataFrameExtractor": MockDataFrameExtractor,
        "MockModelExtractor": MockModelExtractor,
        "MockRuleChecker": MockRuleChecker,
    }


def test_inspect(mock_inspector_dependencies):
    # Unpack mocks
    mock_open_file = mock_inspector_dependencies["mock_open"]
    mock_ast_parse = mock_inspector_dependencies["mock_ast_parse"]
    MockLibraryExtractor = mock_inspector_dependencies["MockLibraryExtractor"]
    MockVariableExtractor = mock_inspector_dependencies[
        "MockVariableExtractor"
    ]
    MockDataFrameExtractor = mock_inspector_dependencies[
        "MockDataFrameExtractor"
    ]
    MockModelExtractor = mock_inspector_dependencies["MockModelExtractor"]
    MockRuleChecker = mock_inspector_dependencies["MockRuleChecker"]

    # Setup mock objects
    mock_rule_checker = MockRuleChecker.return_value
    mock_library_extractor = MockLibraryExtractor.return_value
    mock_variable_extractor = MockVariableExtractor.return_value
    mock_data_frame_extractor = MockDataFrameExtractor.return_value
    mock_model_extractor = MockModelExtractor.return_value

    # Configure mocks with return values
    mock_library_extractor.get_library_aliases.return_value = {"pandas": "pd"}
    mock_variable_extractor.extract_variable_definitions.return_value = [
        "var1",
        "var2",
    ]
    mock_data_frame_extractor.extract_dataframe_variables.return_value = [
        "df_var1",
        "df_var2",
    ]
    mock_model_extractor.model_dict = {"model1": "details"}
    mock_model_extractor.tensor_operations_dict = {
        "operation": ["tensor_op1", "tensor_op2"]
    }
    mock_model_extractor.load_model_methods.return_value = {
        "method1": "details"
    }

    mock_rule_checker.rule_check.return_value = pd.DataFrame(
        data=[
            [
                "mock_file.py",
                "my_function",
                "smell1",
                10,
                "description1",
                "info1",
            ],
            [
                "mock_file.py",
                "my_function",
                "smell2",
                15,
                "description2",
                "info2",
            ],
        ],
        columns=[
            "filename",
            "function_name",
            "smell_name",
            "line",
            "description",
            "additional_info",
        ],
    )

    # Mock file contents
    mock_file_contents = """\
import pandas as pd

def my_function():
    df = pd.DataFrame()
    return df
"""
    mock_open_file.return_value.read.return_value = mock_file_contents

    # Mock AST parsing to simulate a function definition
    mock_ast_parse.return_value = ast.Module(
        body=[
            ast.FunctionDef(
                name="my_function",
                args=ast.arguments(
                    args=[],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                ),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id="df", ctx=ast.Store())],
                        value=ast.Call(
                            func=ast.Name(id="pd.DataFrame", ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                    )
                ],
                decorator_list=[],
                lineno=1,
            )
        ]
    )

    # Instantiate the Inspector class
    inspector = Inspector(output_path="mock_output_path")
    inspector.rule_checker = mock_rule_checker

    # Call the `inspect` method
    result = inspector.inspect("mock_file.py")

    # Assertions
    mock_open_file.assert_called_once_with(
        os.path.abspath("mock_file.py"), "r", encoding="utf-8"
    )
    mock_ast_parse.assert_called_once()
    mock_rule_checker.rule_check.assert_called_once()

    # Check result type and structure
    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "filename",
        "function_name",
        "smell_name",
        "line",
        "description",
        "additional_info",
    ]
    assert list(result.columns) == expected_columns
    assert len(result) > 0
