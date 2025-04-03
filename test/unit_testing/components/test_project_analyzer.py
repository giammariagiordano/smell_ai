import os
import shutil
import pytest
import pandas as pd
from unittest.mock import ANY, MagicMock, patch
from components.project_analyzer import ProjectAnalyzer


@pytest.fixture
def mock_output_path(tmp_path):
    """
    Pytest fixture to create a temporary output directory.
    """
    return str(tmp_path)


@pytest.fixture
def project_analyzer(mock_output_path):
    """
    Fixture to create an instance of ProjectAnalyzer.
    """
    return ProjectAnalyzer(output_path=mock_output_path)


@pytest.fixture
def mock_file_related_methods(monkeypatch):
    """
    Fixture to mock the file-related methods.
    This fixture reduces repetition
    for mocking methods like os.path, FileUtils, etc.
    """
    monkeypatch.setattr("os.path.isdir", lambda path: True)
    monkeypatch.setattr("os.listdir", lambda path: ["project1", "project2"])
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.get_python_files",
        lambda path: ["file1.py"],
    )
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.initialize_log", lambda path: None
    )
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.synchronized_append_to_log",
        lambda path, project, lock: None,
    )


def test_analyze_project(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test the `analyze_project` method.
    """

    output_dir = tmp_path / "output"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: df.to_csv(
            output_dir / "overview.csv", index=False
        ),
    )

    # Mock inspection results for two files
    mock_inspection_results = [
        pd.DataFrame(
            {
                "filename": ["file1.py"],
                "function_name": ["func1"],
                "smell_name": ["smell1"],
                "line": [10],
                "description": ["desc1"],
                "additional_info": ["info1"],
            }
        ),
        pd.DataFrame(
            {
                "filename": ["file2.py"],
                "function_name": ["func2"],
                "smell_name": ["smell2"],
                "line": [20],
                "description": ["desc2"],
                "additional_info": ["info2"],
            }
        ),
    ]

    # Mock inspect method to return the inspection results
    project_analyzer.inspector.inspect = MagicMock(
        side_effect=mock_inspection_results
    )

    # Mock the get_python_files method to return both files
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.get_python_files",
        lambda _: ["file1.py", "file2.py"],
    )

    # Run the method
    total_smells = project_analyzer.analyze_project(
        "test/unit_testing/components/mock_project_path"
    )

    # Assertions
    assert total_smells == 2  # Expecting 2 smells (from file1.py and file2.py)
    project_analyzer.inspector.inspect.assert_any_call("file1.py")
    project_analyzer.inspector.inspect.assert_any_call("file2.py")

    mock_project_path = "test/unit_testing/components/mock_project_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_analyze_projects_sequential(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test the `analyze_projects_sequential` method.
    """

    output_dir = tmp_path / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: df.to_csv(
            output_dir / "overview.csv", index=False
        ),
    )

    # Mock the inspector's inspect method
    mock_inspection_results = pd.DataFrame(
        {
            "filename": ["file1.py"],
            "function_name": ["func1"],
            "smell_name": ["smell1"],
            "line": [10],
        }
    )
    project_analyzer.inspector.inspect = MagicMock(
        return_value=mock_inspection_results
    )

    # Call the method
    project_analyzer.analyze_projects_sequential(
        "test/unit_testing/components/mock_project_path", resume=False
    )

    # Ensure inspect was called
    project_analyzer.inspector.inspect.assert_called_with("file1.py")

    mock_project_path = "test/unit_testing/components/mock_project_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_clean_output_directory(monkeypatch, project_analyzer):
    """
    Test the `clean_output_directory` method.
    """
    mock_clean_directory = MagicMock()
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.clean_directory", mock_clean_directory
    )

    # Run the method
    project_analyzer.clean_output_directory()

    # Assertions
    mock_clean_directory.assert_called_once_with(
        project_analyzer.base_output_path, "output"
    )


def test_merge_all_results(monkeypatch, project_analyzer):
    """
    Test the `merge_all_results` method.
    """
    mock_merge_results = MagicMock()
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.merge_results", mock_merge_results
    )

    # Run the method
    project_analyzer.merge_all_results()

    # Assertions
    mock_merge_results.assert_called_once_with(
        input_dir=os.path.join(
            project_analyzer.output_path, "project_details"
        ),
        output_dir=project_analyzer.output_path,
    )


def test_analyze_projects_parallel(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test the `analyze_projects_parallel` method.
    """

    mock_inspection_results = pd.DataFrame(
        {
            "filename": ["file1.py"],
            "function_name": ["func1"],
            "smell_name": ["smell1"],
            "line": [10],
            "description": ["desc1"],
            "additional_info": ["info1"],
        }
    )

    # Mock dependencies
    monkeypatch.setattr(
        "os.path.exists", lambda path: True  # Mock that all paths exist
    )
    monkeypatch.setattr(
        "os.path.isdir",
        lambda path: True,  # Mock that all paths are directories
    )

    # Mock the inspector's inspect method
    project_analyzer.inspector.inspect = MagicMock(
        return_value=mock_inspection_results
    )

    # Mock save results method
    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: None,  # Do nothing on saving results
    )

    # Mock ThreadPoolExecutor to avoid threading and run tasks synchronously
    with patch("concurrent.futures.ThreadPoolExecutor") as MockExecutor:
        mock_executor = MagicMock()
        MockExecutor.return_value = mock_executor
        mock_executor.__enter__.return_value = mock_executor
        # Make sure the function gets executed immediately (synchronously)
        mock_executor.submit.side_effect = lambda func, *args, **kwargs: func(
            *args, **kwargs
        )

        # Run the method
        with patch("builtins.print") as mock_print:
            project_analyzer.analyze_projects_parallel(
                "test/unit_testing/components/mock_base_path", max_workers=1
            )

        # Ensure the inspector's inspect method
        # was called the expected number of times
        assert project_analyzer.inspector.inspect.call_count == 2

        # Check if print statements were made (optional)
        assert mock_print.call_count > 0


def test_exception_handling_in_inspect(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test that the `inspect` method handles exceptions gracefully.
    """

    # Simulate an exception in the inspect method
    project_analyzer.inspector.inspect = MagicMock(
        side_effect=FileNotFoundError
    )

    with patch("builtins.print") as mock_print:
        project_analyzer.analyze_projects_parallel(
            "test/unit_testing/components/mock_project_path", max_workers=1
        )

    # Assertions
    assert (
        "Total code smells found in all projects: 0\n"
        in mock_print.call_args[0][0]
    )

    mock_project_path = "test/unit_testing/components/mock_project_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_analyze_project_with_errors(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test `analyze_project` with error
    handling (FileNotFoundError, SyntaxError).
    """
    output_dir = tmp_path / "output"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: df.to_csv(
            output_dir / "overview.csv", index=False
        ),
    )

    # Mocking a SyntaxError for a specific file
    project_analyzer.inspector.inspect = MagicMock(side_effect=SyntaxError)

    # Run the method (simulate failure for file1.py)
    project_analyzer.analyze_project(
        "test/unit_testing/components/mock_project_path"
    )

    # Check if the error is logged to the error.txt file
    error_file = output_dir / "error.txt"
    with open(error_file, "r") as f:
        error_content = f.read()

    assert (
        "Error in file file1.py: " in error_content
    )  # Check that error is logged

    mock_project_path = "test/unit_testing/components/mock_project_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_analyze_projects_sequential_save_results(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test saving results in `project_details` for sequential analysis.
    """
    output_dir = tmp_path / "output"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: df.to_csv(
            output_dir / "overview.csv", index=False
        ),
    )

    # Mock the inspector's inspect method
    mock_inspection_results = pd.DataFrame(
        {
            "filename": ["file1.py"],
            "function_name": ["func1"],
            "smell_name": ["smell1"],
            "line": [10],
        }
    )
    project_analyzer.inspector.inspect = MagicMock(
        return_value=mock_inspection_results
    )

    # Call the method
    project_analyzer.analyze_projects_sequential(
        "test/unit_testing/components/mock_project_path", resume=False
    )

    # Check if project_details directory and the result file were created
    details_path = output_dir / "project_details"
    assert details_path.exists()

    detailed_file_path = details_path / "project1_results.csv"
    assert detailed_file_path.exists()

    # Check if the CSV file contains the expected data
    df = pd.read_csv(detailed_file_path)
    assert not df.empty
    assert "filename" in df.columns
    assert df["filename"].iloc[0] == "file1.py"

    mock_project_path = "test/unit_testing/components/mock_project_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_analyze_projects_parallel_thread_safety(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test thread-safety in the `analyze_projects_parallel` method.
    """

    mock_inspection_results = pd.DataFrame(
        {
            "filename": ["file1.py"],
            "function_name": ["func1"],
            "smell_name": ["smell1"],
            "line": [10],
            "description": ["desc1"],
            "additional_info": ["info1"],
        }
    )

    # Mock the inspector's inspect method
    project_analyzer.inspector.inspect = MagicMock(
        return_value=mock_inspection_results
    )

    # Mock the synchronized_append_to_log method to check for thread-safety
    mock_synchronized_append = MagicMock()
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.synchronized_append_to_log",
        mock_synchronized_append,
    )

    # Run the method with parallel execution
    project_analyzer.analyze_projects_parallel(
        "test/unit_testing/components/mock_base_path", max_workers=2
    )

    # Normalize the paths for cross-platform consistency
    expected_path = os.path.join(
        "test/unit_testing/components/mock_base_path", "execution_log.txt"
    )

    # Ensure the synchronized_append_to_log
    # method was called with both project1 and project2
    mock_synchronized_append.assert_any_call(expected_path, "project1", ANY)
    mock_synchronized_append.assert_any_call(expected_path, "project2", ANY)

    mock_project_path = "test/unit_testing/components/mock_base_path"
    if os.path.exists(mock_project_path):
        shutil.rmtree(mock_project_path)


def test_analyze_project_empty_directory(
    monkeypatch, project_analyzer, mock_file_related_methods, tmp_path
):
    """
    Test `analyze_project` when no Python files exist in the directory.
    """
    output_dir = tmp_path / "output"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    monkeypatch.setattr(
        "components.project_analyzer.ProjectAnalyzer._save_results",
        lambda self, df, path: df.to_csv(
            output_dir / "overview.csv", index=False
        ),
    )

    # Mock get_python_files to return an empty list
    monkeypatch.setattr(
        "utils.file_utils.FileUtils.get_python_files", lambda _: []
    )

    # Run the method
    total_smells = project_analyzer.analyze_project(
        "test/unit_testing/components/mock_project_path"
    )

    # Assert that no smells are found
    assert total_smells == 0
