import argparse
import sys
from components.project_analyzer import ProjectAnalyzer


class CodeSmileCLI:
    """
    Manages the overall analysis workflow.
    """

    def __init__(self, args):
        """
        Initializes the CLI with parsed arguments.

        Parameters:
        - args: Parsed CLI arguments.
        """
        self.args = args
        self.analyzer = ProjectAnalyzer(args.output)

    def validate_args(self):
        """
        Validates the command-line arguments
        before proceeding with the analysis.
        """
        if self.args.input is None:
            print("Error: Please specify both input and output folders.")
            exit(1)

        # Validate max_walkers for parallel execution
        if self.args.parallel and self.args.max_walkers <= 0:
            raise ValueError("max_walkers must be greater than 0.")

    def execute(self):
        """
        Executes the analysis workflow based on CLI arguments.
        """
        # Validate arguments first
        self.validate_args()

        print("Starting analysis with the following configuration:")
        print(f"Input folder: {self.args.input}")
        print(f"Output folder: {self.args.output}")
        print(f"Parallel execution: {self.args.parallel}")
        print(f"Resume execution: {self.args.resume}")
        print(f"Max Walkers: {self.args.max_walkers}")
        print(f"Analyze multiple projects: {self.args.multiple}")

        if not self.args.resume:
            self.analyzer.clean_output_directory()

        if self.args.multiple:
            if self.args.parallel:
                self.analyzer.analyze_projects_parallel(
                    self.args.input, self.args.max_walkers
                )
            else:
                self.analyzer.analyze_projects_sequential(
                    self.args.input, resume=self.args.resume
                )
        else:
            total_smells = self.analyzer.analyze_project(self.args.input)
            print(
                f"Analysis completed. Total code smells found: {total_smells}"
            )

        if self.args.multiple:
            self.analyzer.merge_all_results()

        print("Analysis results saved successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Code Smile: AI-specific "
        "code smells detector for Python projects."
    )
    parser.add_argument(
        "--input", type=str, help="Path to the input folder", required=True
    )
    parser.add_argument(
        "--output", type=str, help="Path to the output folder", required=True
    )
    parser.add_argument(
        "--max_walkers",
        type=int,
        default=5,
        help="Number of workers for parallel execution (default: 5)",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel execution (default: False)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume previous execution (default: False)",
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Analyze multiple projects (default: False)",
    )

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        # SystemExit will be raised automatically for missing arguments
        print("Error: Missing required arguments or invalid input.\n")
        parser.print_help()
        sys.exit(1)

    # Execute main logic
    print("Starting Code Smile analysis...")
    manager = CodeSmileCLI(args)
    manager.execute()


if __name__ == "__main__":
    main()
