import pytest
from unittest.mock import Mock, patch
from tkinter import Tk
from gui.code_smell_detector_gui import CodeSmellDetectorGUI


@pytest.fixture
def gui_setup():
    root = Tk()
    gui = CodeSmellDetectorGUI(root)
    return gui


@patch("gui.code_smell_detector_gui.ProjectAnalyzer")
def test_gui_calls_project_analyzer(mock_analyzer, gui_setup):
    mock_instance = Mock()
    mock_instance.analyze_project.return_value = 5
    mock_analyzer.return_value = mock_instance

    gui_setup.input_path.configure(text="/fake/input")
    gui_setup.output_path.configure(text="/fake/output")

    gui_setup.run_analysis(
        input_path="/fake/input",
        output_path="/fake/output",
        num_walkers=1,
        is_parallel=False,
        is_resume=False,
        is_multiple=False,
    )

    mock_instance.analyze_project.assert_called_once_with("/fake/input")
    print("Test Passed: GUI → ProjectAnalyzer")
