import pytest
from unittest.mock import patch
import pandas as pd
from components.inspector import Inspector


@pytest.fixture
def inspector_setup(tmp_path):
    # Crea un file Python fittizio
    input_file = tmp_path / "test_file.py"
    input_file.write_text(
        """
import pandas as pd

def process_data():
    # Creazione di un DataFrame
    df = pd.DataFrame([1, 2, 3])
    df['new_col'] = df[0] + 1
"""
    )
    return str(input_file)


@patch("components.inspector.RuleChecker")
@patch("components.inspector.LibraryExtractor")
@patch("components.inspector.DataFrameExtractor")
@patch("components.inspector.ModelExtractor")
@patch("components.inspector.VariableExtractor")
def test_inspector_to_rulechecker(
    mock_variable_extractor,
    mock_model_extractor,
    mock_dataframe_extractor,
    mock_library_extractor,
    mock_rule_checker,
    inspector_setup,
):
    mock_library_extractor.return_value.extract_libraries.return_value = [
        {"name": "pandas", "alias": "pd"}
    ]
    mock_dataframe_instance = mock_dataframe_extractor.return_value
    mock_dataframe_instance.extract_dataframe_variables.return_value = ["df"]

    mock_variable_instance = mock_variable_extractor.return_value
    mock_variable_instance.extract_variable_definitions.return_value = {
        "df": "MockedNode"
    }
    mock_model_extractor.return_value.model_dict = {}

    mock_rule_checker.return_value.rule_check.return_value = pd.DataFrame(
        [
            {
                "filename": "test_file.py",
                "function_name": "main",
                "smell_name": "MockedSmell",
                "line": 3,
                "description": "Mocked smell detected",
                "additional_info": "None",
            }
        ]
    )

    inspector = Inspector(output_path="output")

    result = inspector.inspect(inspector_setup)

    mock_library_extractor.return_value.extract_libraries.assert_called_once()
    mock_dataframe_instance = mock_dataframe_extractor.return_value
    mock_dataframe_instance.extract_dataframe_variables.assert_called_once()
    mock_variable_instance = mock_variable_extractor.return_value
    mock_variable_instance.extract_variable_definitions.assert_called_once()

    mock_model_extractor.return_value.load_model_dict.assert_called_once()

    mock_rule_checker.return_value.rule_check.assert_called_once()

    assert not result.empty
    assert "smell_name" in result.columns
    assert result["smell_name"].iloc[0] == "MockedSmell"
    print("Test Passed: Inspector → RuleChecker Integration")
