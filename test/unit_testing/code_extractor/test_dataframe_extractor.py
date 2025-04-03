import pytest
import ast
from io import StringIO
from code_extractor import dataframe_extractor
import textwrap


@pytest.fixture
def extractor():
    """
    Create and return an instance of
    DataFrameExtractor with loaded methods.
    """
    method_csv = StringIO("method\nhead\nmerge\n")
    extractor = dataframe_extractor.DataFrameExtractor()
    extractor.load_dataframe_dict(method_csv)
    return extractor


@pytest.fixture
def sample_code():
    return textwrap.dedent(
        """
        import pandas as pd

        def test_function(df, other_df):
            df = pd.DataFrame({'a': [1, 2, 3]})
            other_df = df.head()
            result = other_df.merge(df, on='a')
            print(df['a'])
        """
    )


@pytest.fixture
def empty_function_code():
    return "def empty_function(): pass"


@pytest.fixture
def nested_calls_code():
    return textwrap.dedent(
        """
        import pandas as pd
        def nested_function():
            df = pd.DataFrame({'a': [1, 2, 3]}).head()
            result = df.merge(df, on='a')
            print(df['a'])
    """
    )


@pytest.fixture
def no_pandas_alias_code():
    return textwrap.dedent(
        """
        import pandas
        def no_alias_function():
            df = pandas.DataFrame({'a': [1, 2, 3]})
    """
    )


@pytest.fixture
def complex_subscript_access_code():
    return textwrap.dedent(
        """
        import pandas as pd
        def complex_access_function():
            df = pd.DataFrame({'a': [1, 2, 3]})
            col = 'a'
            print(df[col])
    """
    )


def parse_function(code):
    """Helper method to parse code and extract the function node."""
    tree = ast.parse(code)
    return next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    )


def test_load_dataframe_dict(extractor):
    """Test loading of DataFrame methods from a CSV."""
    assert extractor.df_methods == ["head", "merge"]


def test_extract_dataframe_variables(extractor, sample_code):
    """Test extraction of DataFrame variables."""
    function_node = parse_function(sample_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    assert sorted(dataframe_vars) == ["df", "other_df", "result"]


def test_track_dataframe_methods(extractor, sample_code):
    """Test tracking of DataFrame methods."""
    function_node = parse_function(sample_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    method_usage = extractor.track_dataframe_methods(
        function_node, dataframe_vars
    )
    assert method_usage == {
        "df": ["head"],
        "other_df": ["merge"],
        "result": [],
    }


def test_track_dataframe_accesses(extractor, sample_code):
    """Test tracking of DataFrame column accesses."""
    function_node = parse_function(sample_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    accesses = extractor.track_dataframe_accesses(
        function_node, dataframe_vars
    )
    assert accesses == {"df": ["a"], "other_df": [], "result": []}


def test_empty_function(extractor, empty_function_code):
    """Test with an empty function node."""
    function_node = parse_function(empty_function_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    assert dataframe_vars == []

    method_usage = extractor.track_dataframe_methods(
        function_node, dataframe_vars
    )
    assert method_usage == {}

    accesses = extractor.track_dataframe_accesses(
        function_node, dataframe_vars
    )
    assert accesses == {}


def test_nested_dataframe_calls(extractor, nested_calls_code):
    """Test nested DataFrame calls."""
    function_node = parse_function(nested_calls_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    assert sorted(dataframe_vars) == ["df", "result"]

    method_usage = extractor.track_dataframe_methods(
        function_node, dataframe_vars
    )
    assert method_usage == {
        "df": ["merge"],
        "result": [],
    }

    accesses = extractor.track_dataframe_accesses(
        function_node, dataframe_vars
    )
    assert accesses == {"df": ["a"], "result": []}


def test_no_pandas_alias(extractor, no_pandas_alias_code):
    """Test function that uses Pandas without aliasing."""
    function_node = parse_function(no_pandas_alias_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    assert dataframe_vars == []


def test_complex_subscript_access(extractor, complex_subscript_access_code):
    """Test for DataFrame accesses with non-constant keys."""
    function_node = parse_function(complex_subscript_access_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )
    accesses = extractor.track_dataframe_accesses(
        function_node, dataframe_vars
    )

    # Non-constant keys should not be tracked
    assert accesses == {"df": []}


def test_malformed_csv(extractor):
    """Test loading a malformed CSV file."""
    malformed_csv = StringIO("not_method_column\nhead\nmerge\n")
    with pytest.raises(KeyError):
        extractor.load_dataframe_dict(malformed_csv)


def test_large_ast(extractor):
    """Test handling of a large AST."""
    large_code = "\n".join(
        [f"def function_{i}(): df = pd.DataFrame()" for i in range(1000)]
    )
    tree = ast.parse(large_code)

    for function_node in [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]:
        dataframe_vars = extractor.extract_dataframe_variables(
            function_node, alias="pd"
        )
        assert dataframe_vars == ["df"]


def test_aliasing_dataframe_name(extractor, mocker):
    """Test when DataFrame is assigned to another variable."""
    aliasing_code = textwrap.dedent(
        """
        import pandas as pd
        def aliasing_function():
            df1 = pd.DataFrame({'a': [1, 2, 3]})
            df2 = df1
    """
    )
    function_node = parse_function(aliasing_code)
    dataframe_vars = extractor.extract_dataframe_variables(
        function_node, alias="pd"
    )

    # Using mocker to mock the `df1` and `df2` assignments
    mocker.patch.object(
        extractor, "extract_dataframe_variables", return_value=["df1", "df2"]
    )

    assert sorted(dataframe_vars) == ["df1", "df2"]
