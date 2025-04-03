import io
import os
import pytest
import pandas as pd
from report.report_generator import ReportGenerator


@pytest.fixture
def mock_data():
    """
    Fixture that provides a mock DataFrame to simulate CSV file content.
    """
    return pd.DataFrame(
        {
            "filename": ["file1.py", "file2.py", "file3.py", "file4.py"],
            "smell_name": [
                "Long Method",
                "Duplicated Code",
                "Long Method",
                "Duplicated Code",
            ],
        }
    )


@pytest.fixture
def mock_file_paths():
    """
    Fixture to simulate file paths that would
    be processed by the report generator.
    """
    return [
        os.path.normpath("test_project_details/smell_data_1.csv"),
        os.path.normpath("test_project_details/smell_data_2.csv"),
    ]


@pytest.fixture
def generator():
    """
    Fixture to instantiate the ReportGenerator object.
    """
    return ReportGenerator(
        input_path=os.path.normpath("test_project_details"),
        output_path=os.path.normpath("test_output"),
    )


def test_load_data(generator, mock_data, mocker, mock_file_paths):
    """
    Test the `_load_data` function that reads CSV files and concatenates them.
    """
    mocker.patch("pandas.read_csv", return_value=mock_data)

    df = generator._load_data(mock_file_paths)

    assert len(df) == len(mock_data) * len(mock_file_paths)


def test_find_project_details(generator, mocker):
    """
    Test the `_find_project_details` method to
    verify it finds the project details folder and files.
    """
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch(
        "os.listdir", return_value=["smell_data_1.csv", "smell_data_2.csv"]
    )

    file_paths = generator._find_project_details()

    assert len(file_paths) == 2
    assert file_paths[0].endswith("smell_data_1.csv")


def test_smell_report(generator, mock_data, mocker):
    """
    Test the `smell_report` method to ensure
    it generates and saves the correct report.
    """
    pandas_to_csv_call = mocker.patch("pandas.DataFrame.to_csv")

    generator.smell_report(mock_data)

    output_path = os.path.normpath("test_output/general_overview.csv")
    pandas_to_csv_call.assert_called_with(output_path, index=False)


def test_project_report(generator, mock_data, mocker):
    """
    Test the `project_report` method to verify
    it generates and saves the correct project report.
    """
    mock_data["project_name"] = [
        "project1",
        "project2",
        "project1",
        "project2",
    ]

    pandas_to_csv_call = mocker.patch("pandas.DataFrame.to_csv")

    generator.project_report(mock_data)

    output_path = os.path.normpath("test_output/project_overview.csv")
    pandas_to_csv_call.assert_called_with(output_path, index=False)


def test_summary_report(generator, mock_data, mocker):
    """
    Test the `summary_report` method to ensure it
    generates and saves the correct summary Excel report.
    """
    mock_data["project_name"] = [
        "project1",
        "project2",
        "project1",
        "project2",
    ]

    mock_excel_writer = mocker.patch("pandas.ExcelWriter", autospec=True)

    mock_file = io.BytesIO()
    mock_excel_writer.return_value.__enter__.return_value = mock_file

    mock_file.seek = mocker.MagicMock()

    generator.summary_report(mock_data)

    mock_file.seek.assert_called()


def test_visualize_smell_report(generator, mock_data, mocker):
    """
    Test the `visualize_smell_report` method
    to ensure it generates and saves the correct plot.
    """
    mock_savefig = mocker.patch("matplotlib.pyplot.savefig")

    output_path = os.path.normpath("test_output/smell_report_chart.png")
    generator.visualize_smell_report(mock_data)

    mock_savefig.assert_called_with(output_path)


def test_menu(mocker):
    """
    Test the `menu` method to simulate user input and verify the response.
    """
    mocker.patch("builtins.input", return_value="1")

    generator = ReportGenerator(
        input_path=os.path.normpath("test_project_details"),
        output_path=os.path.normpath("test_output"),
    )

    choice = generator.menu()
    assert choice == "1"
