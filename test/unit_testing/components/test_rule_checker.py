import pytest
import pandas as pd
import ast
from components.rule_checker import RuleChecker


@pytest.fixture
def mock_rule_checker():
    return RuleChecker(output_path="mock_output_path")


@pytest.fixture
def mock_ast_node(mocker):
    # Create mock AST node with real ast.AST objects for fields
    mock_node = mocker.Mock(spec=ast.AST)

    mock_node._fields = ["field1", "field2"]

    mock_node.field1 = ast.Name(id="df", ctx=ast.Load())
    mock_node.field2 = ast.Str(s="some_string")

    return mock_node


@pytest.fixture
def df_output():
    return pd.DataFrame(
        columns=[
            "filename",
            "function_name",
            "smell_name",
            "line",
            "description",
            "additional_info",
        ]
    )


def test_rule_check(mocker, mock_rule_checker, mock_ast_node, df_output):
    # Mock the classes for DataFrameConversionAPIMisused and ChainIndexingSmell
    mock_dataframe_conversion = mocker.Mock()
    mock_chain_indexing = mocker.Mock()

    # Mocking the return value of detect for
    #  DataFrameConversionAPIMisused
    #  (no smells for now)
    mock_dataframe_conversion.detect.return_value = []

    # Mocking the return value of detect
    # for ChainIndexingSmell (smells detected)
    mock_chain_indexing.detect.return_value = [
        {
            "name": "Chained indexing detected",
            "line": 12,
            "description": "Using chained indexing like df['a'][0] "
            " can cause performance issues and unexpected behavior.",
            "additional_info": "Use df.loc[0, 'a'] for more "
            "efficient and explicit indexing.",
        },
    ]

    # Add mocked smells to mock_rule_checker
    mock_rule_checker.smells = [mock_chain_indexing, mock_dataframe_conversion]

    # Populate extracted_data with chained indexing example
    extracted_data = {
        "libraries": {
            "pandas": "pd",  # Pandas library alias
        },
        "variables": {
            "df": ast.Assign(
                targets=[ast.Name(id="df", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="pd", ctx=ast.Load()),
                        attr="DataFrame",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Dict(
                            keys=[ast.Str(s="a")],
                            values=[
                                ast.List(
                                    elts=[
                                        ast.Constant(value=1),
                                        ast.Constant(value=2),
                                        ast.Constant(value=3),
                                    ],
                                    ctx=ast.Load(),
                                )
                            ],
                        )
                    ],
                    keywords=[],
                ),
            ),
            "chained_indexing_example": ast.Assign(
                targets=[
                    ast.Name(id="chained_indexing_example", ctx=ast.Store())
                ],
                value=ast.Subscript(
                    value=ast.Subscript(
                        value=ast.Name(id="df", ctx=ast.Load()),
                        slice=ast.Str(s="a"),
                        ctx=ast.Load(),
                    ),
                    slice=ast.Constant(value=0),
                    ctx=ast.Load(),
                ),
            ),
        },
        "lines": {
            1: "import pandas as pd",
            2: "df = pd.DataFrame({'a': [1, 2, 3]})",
            3: "chained_indexing_example = df['a'][0]",
        },
    }

    # Run the rule_check method
    filename = "mock_file.py"
    function_name = "my_function"
    result = mock_rule_checker.rule_check(
        mock_ast_node, extracted_data, filename, function_name, df_output
    )

    # Debug prints
    print("Mock detect return values:")
    print(mock_dataframe_conversion.detect.return_value)
    print(mock_chain_indexing.detect.return_value)
    print("Result DataFrame:")
    print(result)

    # Assertions to verify if the smells were added correctly
    assert (
        len(result) == 1
    )  # Expecting one smell (chained indexing) to be detected


def test_no_smells(mocker, mock_rule_checker, mock_ast_node, df_output):
    # Mock the chain indexing detection method to return no smells
    mock_chain_smell = mocker.patch(
        "detection_rules.api_specific.chain_indexing_smell.ChainIndexingSmell",
        autospec=True,
    )
    mock_chain_smell.return_value.detect.return_value = (
        []
    )  # Ensure it returns an empty list

    # Mocking extracted_data
    extracted_data = {
        "libraries": {"pandas": "pd"},
        "dataframe_variables": {},
        "other_data": "some_value",
    }

    filename = "mock_file.py"
    function_name = "my_function"

    result = mock_rule_checker.rule_check(
        ast_node=mock_ast_node,
        extracted_data=extracted_data,
        filename=filename,
        function_name=function_name,
        df_output=df_output,
    )

    # Assertions
    assert len(result) == 0  # No smells detected
