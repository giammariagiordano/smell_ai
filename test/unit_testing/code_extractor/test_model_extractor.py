import pytest
from unittest.mock import MagicMock
import pandas as pd
from code_extractor.model_extractor import ModelExtractor


@pytest.fixture
def extractor():
    """Fixture to create and return a ModelExtractor instance."""
    return ModelExtractor("models.csv", "tensors.csv")


def test_load_model_dict(mocker, extractor):
    """Test loading the model dictionary from a CSV file."""
    # Setup mock
    mock_exists = mocker.patch("os.path.exists", return_value=True)
    mock_read_csv = mocker.patch("pandas.read_csv")
    mock_df = MagicMock()
    mock_df.columns = ["method", "library"]
    mock_df.to_dict.return_value = {"method": ["method1"], "library": ["lib1"]}
    mock_read_csv.return_value = mock_df

    model_dict = extractor.load_model_dict()

    assert model_dict == {"method": ["method1"], "library": ["lib1"]}
    mock_exists.assert_called_once_with("models.csv")
    mock_read_csv.assert_called_once_with("models.csv")


def test_load_model_dict_file_not_found(mocker, extractor):
    """Test that FileNotFoundError is raised when model file doesn't exist."""
    mock_exists = mocker.patch(  # noqa: F841
        "os.path.exists", return_value=False
    )

    with pytest.raises(FileNotFoundError):
        extractor.load_model_dict()


def test_load_model_dict_missing_columns(mocker, extractor):
    """Test that ValueError is raised if the expected columns are missing."""
    mock_exists = mocker.patch(  # noqa: F841
        "os.path.exists", return_value=True
    )
    mock_read_csv = mocker.patch("pandas.read_csv")
    mock_df = MagicMock()
    mock_df.columns = ["other_column"]
    mock_read_csv.return_value = mock_df

    with pytest.raises(ValueError):
        extractor.load_model_dict()


def test_load_tensor_operations_dict(mocker, extractor):
    """Test loading the tensor operations dictionary from a CSV file."""
    mock_exists = mocker.patch("os.path.exists", return_value=True)

    df = pd.DataFrame(
        {"number_of_tensors_input": [2, 1], "operation": ["op1", "op2"]}
    )
    mock_read_csv = mocker.patch("pandas.read_csv", return_value=df)

    tensor_dict = extractor.load_tensor_operations_dict()

    expected_dict = {"number_of_tensors_input": [2], "operation": ["op1"]}
    assert tensor_dict == expected_dict
    mock_exists.assert_called_once_with("tensors.csv")
    mock_read_csv.assert_called_once_with("tensors.csv")


def test_load_tensor_operations_dict_file_not_found(mocker, extractor):
    """
    Test that FileNotFoundError is raised
    when tensor operations file doesn't exist.
    """
    mock_exists = mocker.patch(  # noqa: F841
        "os.path.exists", return_value=False
    )
    with pytest.raises(FileNotFoundError):
        extractor.load_tensor_operations_dict()


def test_load_tensor_operations_dict_missing_columns(mocker, extractor):
    """
    Test that ValueError is raised if the
    expected columns are missing in tensor operations CSV.
    """
    mock_exists = mocker.patch(  # noqa: F841
        "os.path.exists", return_value=True
    )
    mock_read_csv = mocker.patch("pandas.read_csv")
    mock_df = MagicMock()
    mock_df.columns = ["other_column"]
    mock_read_csv.return_value = mock_df

    with pytest.raises(ValueError):
        extractor.load_tensor_operations_dict()


def test_load_model_methods(mocker, extractor):
    """Test extracting model methods."""
    extractor.model_dict = {
        "method": ["method1", "method2"],
        "library": ["lib1", "lib2"],
    }

    methods = extractor.load_model_methods()

    assert methods == ["method1", "method2"]


def test_load_model_methods_not_loaded(mocker, extractor):
    """Test that ValueError is raised if model dictionary is not loaded."""
    with pytest.raises(ValueError):
        extractor.load_model_methods()


def test_check_model_method(mocker, extractor):
    """Test checking if a model belongs to a library."""
    extractor.model_dict = {
        "method": ["method1", "method2"],
        "library": ["lib1", "lib2"],
    }

    result = extractor.check_model_method("method1", ["lib1"])

    assert result is True


def test_check_model_method_not_in_library(mocker, extractor):
    """
    Test that check_model_method returns
    False if model is not in the specified library.
    """
    extractor.model_dict = {
        "method": ["method1", "method2"],
        "library": ["lib1", "lib2"],
    }

    result = extractor.check_model_method("method1", ["lib2"])

    assert result is False


def test_check_model_method_not_loaded(mocker, extractor):
    """Test that ValueError is raised if model dictionary is not loaded."""
    with pytest.raises(ValueError):
        extractor.check_model_method("method1", ["lib1"])
