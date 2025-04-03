import pytest
import os
import pandas as pd
from unittest.mock import Mock, patch
from cli.cli_runner import CodeSmileCLI


@pytest.fixture
def integration_setup(tmp_path):
    input_path = tmp_path / "input"
    output_path = tmp_path / "output"

    input_path.mkdir()
    (input_path / "test_file.py").write_text(
        """
import pandas as pd

def process_data():
    # Creazione di un DataFrame
    df = pd.DataFrame([1, 2, 3])
    df['new_col'] = df[0] + 1
"""
    )

    return str(input_path), str(output_path)


@patch("components.rule_checker.RuleChecker.rule_check")
def test_full_integration_with_cli(mock_rule_check, integration_setup):
    mock_rule_check.return_value = pd.DataFrame(
        [
            {
                "filename": "test_file.py",
                "function_name": "process_data",
                "smell_name": "MockedSmell",
                "line": 3,
                "description": "Mocked smell detected",
                "additional_info": "None",
            }
        ]
    )

    input_path, output_path = integration_setup

    args = Mock(
        input=input_path,
        output=output_path,
        max_walkers=1,
        parallel=False,
        resume=False,
        multiple=False,
    )

    cli = CodeSmileCLI(args)

    cli.execute()

    result_file = os.path.join(output_path, "output", "overview.csv")
    assert os.path.exists(result_file), f"File {result_file} non trovato"

    df = pd.read_csv(result_file)
    assert len(df) == 1
    assert df["smell_name"].iloc[0] == "MockedSmell"

    print("Test Passed: Full Integration with CLI")
