import pytest
import ast
from code_extractor.library_extractor import LibraryExtractor


@pytest.fixture
def extractor():
    """Fixture to create and return a LibraryExtractor instance."""
    return LibraryExtractor()


def test_extract_libraries(mocker, extractor):
    """Test extracting libraries from an AST."""
    code = """
import pandas as pd
from numpy import array
from matplotlib import pyplot as plt
    """
    tree = ast.parse(code)
    libraries = extractor.extract_libraries(tree)

    expected_libraries = [
        {"name": "pandas", "alias": "pd"},
        {"name": "numpy.array", "alias": None},
        {"name": "matplotlib.pyplot", "alias": "plt"},
    ]

    assert libraries == expected_libraries


def test_extract_libraries_no_alias(mocker, extractor):
    """Test case where libraries are imported without aliases."""
    code = """
import pandas
import numpy
    """
    tree = ast.parse(code)
    libraries = extractor.extract_libraries(tree)

    expected_libraries = [
        {"name": "pandas", "alias": None},
        {"name": "numpy", "alias": None},
    ]

    assert libraries == expected_libraries


def test_get_library_aliases(mocker, extractor):
    """Test getting library aliases."""
    libraries = [
        {"name": "pandas", "alias": "pd"},
        {"name": "numpy.array", "alias": None},
    ]
    aliases = extractor.get_library_aliases(libraries)

    expected_aliases = {"pandas": "pd", "numpy.array": "numpy.array"}
    assert aliases == expected_aliases


def test_get_library_of_node_method_call(mocker, extractor):
    """Test getting the library for a method call."""
    code = "import pandas as pd; pd.read_csv('file.csv')"
    tree = ast.parse(code)

    # Find the first Call node (method call like `pd.read_csv()`)
    node = None
    for item in tree.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
            node = item.value
            break

    libraries = [
        {"name": "pandas", "alias": "pd"},
        {"name": "numpy.array", "alias": None},
    ]
    aliases = extractor.get_library_aliases(libraries)
    library_name = extractor.get_library_of_node(node, aliases)

    assert library_name == "pandas"


def test_get_library_of_node_function_call(mocker, extractor):
    """Test getting the library for a function call."""
    code = "import pandas as pd; pd.DataFrame()"
    tree = ast.parse(code)

    # Find the first Call node (function call like `pd.DataFrame()`)
    node = None
    for item in tree.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
            node = item.value
            break

    libraries = [
        {"name": "pandas", "alias": "pd"},
        {"name": "numpy.array", "alias": None},
    ]
    aliases = extractor.get_library_aliases(libraries)
    library_name = extractor.get_library_of_node(node, aliases)

    assert library_name == "pandas"


def test_get_library_of_node_unknown(mocker, extractor):
    """
    Test getting 'Unknown' for a node
    that does not belong to any known library.
    """
    code = "print('hello world')"
    tree = ast.parse(code)
    node = tree.body[0].value  # Get the print function call
    libraries = [
        {"name": "pandas", "alias": "pd"},
        {"name": "numpy.array", "alias": None},
    ]
    aliases = extractor.get_library_aliases(libraries)
    library_name = extractor.get_library_of_node(node, aliases)

    assert library_name == "Unknown"


def test_extract_libraries_empty_code(mocker, extractor):
    """Test extracting libraries from empty code."""
    code = ""
    tree = ast.parse(code)
    libraries = extractor.extract_libraries(tree)

    assert libraries == []


def test_get_library_aliases_empty(mocker, extractor):
    """Test getting aliases from an empty list."""
    libraries = []
    aliases = extractor.get_library_aliases(libraries)

    assert aliases == {}


def test_get_library_of_node_empty(mocker, extractor):
    """Test getting the library of an empty AST."""
    node = None  # No node to inspect
    aliases = {}
    library_name = extractor.get_library_of_node(node, aliases)

    assert library_name == "Unknown"
