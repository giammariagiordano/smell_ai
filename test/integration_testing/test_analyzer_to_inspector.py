import pytest
from unittest.mock import Mock, patch
import os
import pandas as pd
from components.project_analyzer import ProjectAnalyzer


@pytest.fixture
def project_analyzer_setup(tmp_path):
    input_path = tmp_path / "input"
    output_path = tmp_path / "output"

    input_path.mkdir()
    (input_path / "test_file1.py").write_text("print('hello world')\n")
    (input_path / "test_file2.py").write_text("x = 1 + 1\n")

    return str(input_path), str(output_path)


@patch("components.project_analyzer.Inspector")
def test_project_analyzer_calls_inspect(
    mock_inspector_class, project_analyzer_setup
):
    mock_instance = Mock()
    mock_instance.inspect.return_value = pd.DataFrame(
        [
            {
                "filename": "test_file1.py",
                "function_name": "main",
                "smell_name": "TestSmell",
                "line": 1,
                "description": "Mocked smell",
                "additional_info": "None",
            }
        ]
    )
    mock_inspector_class.return_value = mock_instance

    input_path, output_path = project_analyzer_setup

    analyzer = ProjectAnalyzer(output_path=output_path)

    total_smells = analyzer.analyze_project(input_path)

    expected_calls = [
        ((str(os.path.join(input_path, "test_file1.py")),),),
        ((str(os.path.join(input_path, "test_file2.py")),),),
    ]
    mock_instance.inspect.assert_has_calls(expected_calls, any_order=True)

    assert total_smells == 2

    result_file = os.path.join(output_path, "output", "overview.csv")
    assert os.path.exists(result_file)

    df = pd.read_csv(result_file)
    assert len(df) == 2
    print("Test Passed: ProjectAnalyzer → Inspector Integration")
