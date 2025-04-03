from unittest.mock import Mock, patch
from cli.cli_runner import CodeSmileCLI


@patch("cli.cli_runner.ProjectAnalyzer")
def test_cli_calls_project_analyzer(mock_analyzer):
    mock_instance = Mock()
    mock_instance.analyze_project.return_value = 5
    mock_analyzer.return_value = mock_instance

    args = Mock(
        input="/fake/input",
        output="/fake/output",
        max_workers=1,
        parallel=False,
        resume=False,
        multiple=False,
    )

    cli = CodeSmileCLI(args)

    cli.execute()

    mock_analyzer.assert_called_once_with("/fake/output")
    mock_instance.analyze_project.assert_called_once_with("/fake/input")

    print("Test Passed: CLI → ProjectAnalyzer")
