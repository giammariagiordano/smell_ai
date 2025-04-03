import pandas as pd
import pytest
from unittest.mock import mock_open, patch, MagicMock
import os
from utils.file_utils import FileUtils


@pytest.fixture
def mock_file_system():
    with patch("os.path.exists") as mock_exists, patch(
        "os.makedirs"
    ) as mock_makedirs, patch("os.listdir") as mock_listdir, patch(
        "shutil.rmtree"
    ) as mock_rmtree, patch(
        "os.unlink"
    ) as mock_unlink:
        yield (
            mock_exists,
            mock_makedirs,
            mock_listdir,
            mock_rmtree,
            mock_unlink,
        )


@pytest.fixture
def mock_walk():
    with patch("os.walk") as mock_walk:
        yield mock_walk


@pytest.fixture
def mock_merge():
    with patch("os.makedirs") as mock_makedirs, patch(
        "os.walk"
    ) as mock_walk, patch("pandas.read_csv") as mock_read_csv, patch(
        "pandas.DataFrame.to_csv"
    ) as mock_to_csv:
        yield mock_makedirs, mock_walk, mock_read_csv, mock_to_csv


def test_clean_directory(mock_file_system):
    mock_exists, mock_makedirs, mock_listdir, mock_rmtree, mock_unlink = (
        mock_file_system
    )

    # Case 1: Directory exists and has files
    mock_exists.return_value = True
    mock_listdir.return_value = ["file1.txt", "file2.txt"]

    root_path = "mock/root"
    subfolder_name = "output"

    # Call the method
    cleaned_path = FileUtils.clean_directory(root_path, subfolder_name)

    # Assert os.makedirs was not called
    mock_makedirs.assert_not_called()

    # Assert the method returns the correct path
    assert cleaned_path == os.path.join(root_path, subfolder_name)

    # Case 2: Directory does not exist
    mock_exists.return_value = False
    mock_listdir.return_value = []

    # Call the method again
    cleaned_path = FileUtils.clean_directory(root_path, subfolder_name)

    # Assert os.makedirs was called to create the directory
    mock_makedirs.assert_called_with(os.path.join(root_path, subfolder_name))
    assert cleaned_path == os.path.join(root_path, subfolder_name)


def test_get_python_files(mock_walk):
    # Mock os.walk to simulate directory structure
    mock_walk.return_value = [
        ("root", ["subdir1", "subdir2"], ["file1.py", "file2.txt"]),
        ("root/subdir1", [], ["file3.py"]),
        ("root/subdir2", [], ["file4.py"]),
    ]

    path = "root"

    # Call the method
    python_files = FileUtils.get_python_files(path)

    # Calculate the expected absolute paths dynamically
    expected_files = [
        os.path.abspath(os.path.join("root", "file1.py")),
        os.path.abspath(os.path.join("root/subdir1", "file3.py")),
        os.path.abspath(os.path.join("root/subdir2", "file4.py")),
    ]

    # Assert that only Python files are returned with absolute paths
    assert len(python_files) == 3
    assert expected_files[0] in python_files
    assert expected_files[1] in python_files
    assert expected_files[2] in python_files
    assert (
        os.path.abspath(os.path.join("root", "file2.txt")) not in python_files
    )  # Non-Python file


def test_merge_results(mock_merge):
    mock_makedirs, mock_walk, mock_read_csv, mock_to_csv = mock_merge

    # Mock os.walk to simulate the directory structure and files
    mock_walk.return_value = [("mock_input", [], ["file1.csv", "file2.csv"])]

    # Mock pandas read_csv for the two files
    mock_read_csv.side_effect = [
        pd.DataFrame({"filename": ["file1"], "data": [1]}),  # Not empty
        pd.DataFrame({"filename": ["file2"], "data": [2]}),  # Not empty
    ]

    # Mock to_csv (no actual file writing will occur)
    mock_to_csv.return_value = None

    input_dir = "mock_input"
    output_dir = "mock_output"

    # Call the method
    FileUtils.merge_results(input_dir, output_dir)

    # Assert that makedirs was called for the output directory
    mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)

    # Assert that to_csv was called to
    # save the merged result to the correct file
    mock_to_csv.assert_called_once_with(
        os.path.join(output_dir, "overview.csv"), index=False
    )


def test_initialize_log():
    log_path = "mock_log.txt"

    with patch("builtins.open", mock_open()) as mock_file:
        FileUtils.initialize_log(log_path)

        # Assert that the log file is opened in write mode
        mock_file.assert_called_once_with(log_path, "w")
        # Assert that the content written to the log is empty
        mock_file().write.assert_called_once_with("")


def test_append_to_log():
    log_path = "mock_log.txt"
    project_name = "project1"

    with patch("builtins.open", mock_open()) as mock_file:
        FileUtils.append_to_log(log_path, project_name)

        # Assert that the log file is opened in append mode
        mock_file.assert_called_once_with(log_path, "a")
        # Assert that the correct project name was written to the log
        mock_file().write.assert_called_once_with("project1\n")


def test_get_last_logged_project():
    log_path = "mock_log.txt"

    # Case 1: Log file exists and has content
    with patch("builtins.open", mock_open(read_data="project1\nproject2\n")):
        last_project = FileUtils.get_last_logged_project(log_path)
        assert last_project == "project2"

    # Case 2: Log file is empty
    with patch("builtins.open", mock_open(read_data="")):
        last_project = FileUtils.get_last_logged_project(log_path)
        assert last_project == ""

    # Case 3: Log file does not exist
    with patch("builtins.open", side_effect=FileNotFoundError):
        last_project = FileUtils.get_last_logged_project(log_path)
        assert last_project == ""


def test_synchronized_append_to_log():
    log_path = "mock_log.txt"
    project_name = "project1"

    # Create a mock lock
    mock_lock = MagicMock()

    with patch("builtins.open", mock_open()) as mock_file:
        FileUtils.synchronized_append_to_log(log_path, project_name, mock_lock)

        # Assert that the lock was acquired and released
        mock_lock.__enter__.assert_called_once()
        mock_lock.__exit__.assert_called_once()

        # Assert that the log file is opened in append mode
        mock_file.assert_called_once_with(log_path, "a")
        # Assert that the project name was written to the log
        mock_file().write.assert_called_once_with("project1\n")
