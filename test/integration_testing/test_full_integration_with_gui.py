import pytest
import os
import pandas as pd
from tkinter import Tk
from unittest.mock import Mock, patch
from gui.code_smell_detector_gui import CodeSmellDetectorGUI


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


@patch("gui.code_smell_detector_gui.TextBoxRedirect")
@patch("components.rule_checker.RuleChecker.rule_check")
def test_full_integration_with_gui(
    mock_rule_check, mock_textbox_redirect, integration_setup
):
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

    mock_textbox_redirect.return_value.write = Mock()

    input_path, output_path = integration_setup

    root = Tk()
    gui = CodeSmellDetectorGUI(root)

    gui.input_path.configure(text=input_path)
    gui.output_path.configure(text=output_path)

    gui.run_analysis(
        input_path=input_path,
        output_path=output_path,
        num_walkers=1,
        is_parallel=False,
        is_resume=False,
        is_multiple=False,
    )

    result_file = os.path.join(output_path, "output", "overview.csv")

    assert os.path.exists(result_file), f"File {result_file} non trovato"

    df = pd.read_csv(result_file)
    assert len(df) == 1
    assert df["smell_name"].iloc[0] == "MockedSmell"

    root.destroy()

    print("Test Passed: Full Integration (GUI → Smells)")
