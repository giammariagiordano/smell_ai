import os
import time
import threading
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from components.inspector import Inspector
from utils.file_utils import FileUtils


class ProjectAnalyzer:
    """
    Handles the analysis of Python projects
    and manages all file-related operations.
    """

    def __init__(self, output_path: str):
        """
        Initializes the ProjectAnalyzer.

        Parameters:
        - output_path (str): Directory where analysis results will be saved.
        """
        self.base_output_path = output_path
        self.output_path = os.path.join(output_path, "output")

        FileUtils.clean_directory(self.base_output_path, "output")

        self.inspector = Inspector(self.output_path)

    def clean_output_directory(self):
        """
        Cleans or creates the output directory for analysis results.
        """
        FileUtils.clean_directory(self.base_output_path, "output")

    def _save_results(self, df: pd.DataFrame, filename: str):
        """
        Saves the DataFrame to a CSV file in the output root folder.
        """
        if df.empty:
            print(f"No results to save for {filename}")
            return

        os.makedirs(self.output_path, exist_ok=True)

        file_path = os.path.join(self.output_path, filename)
        df.to_csv(file_path, index=False)
        print(f"Results saved to {file_path}")

    def analyze_project(self, project_path: str) -> int:
        """
        Analyzes a single project for code smells.

        Parameters:
        - project_path (str): Path to the project to be analyzed.

        Returns:
        - int: Total number of code smells found in the project.
        """
        project_name = os.path.basename(os.path.normpath(project_path))

        print(f"Starting analysis for project: {project_name}")

        filenames = FileUtils.get_python_files(project_path)
        if not filenames:
            raise ValueError(f"The project '{project_path}' contains no Python files.")
        col = [
            "filename",
            "function_name",
            "smell_name",
            "line",
            "description",
            "additional_info",
        ]
        to_save = pd.DataFrame(columns=col)
        total_smells = 0

        for filename in filenames:
            try:
                result = self.inspector.inspect(filename)

                smell_count = len(result)
                total_smells += smell_count
                if smell_count > 0:
                    print(
                        f"Found {smell_count} code smells in file: {filename}"
                    )
                to_save = pd.concat([to_save, result], ignore_index=True)
            except (SyntaxError, FileNotFoundError) as e:
                error_file = os.path.join(self.output_path, "error.txt")
                os.makedirs(self.output_path, exist_ok=True)
                with open(error_file, "a") as f:
                    f.write(f"Error in file {filename}: {str(e)}\n")
                print(f"Error analyzing file: {filename} - {str(e)}")
                continue

        self._save_results(to_save, "overview.csv")

        print(f"Finished analysis for project: {project_name}")
        print(
            f"Total code smells found in project "
            f"'{project_name}': {total_smells}\n"
        )
        return total_smells

    def analyze_projects_sequential(
        self, base_path: str, resume: bool = False
    ):
        """
        Sequentially analyzes multiple projects.

        Parameters:
        - base_path (str): Directory containing projects to be analyzed.
        - resume (bool): Whether to resume from the last analyzed project.
        """
        execution_log_path = os.path.join(base_path, "execution_log.txt")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if not resume:
            FileUtils.initialize_log(execution_log_path)

        last_project = (
            FileUtils.get_last_logged_project(execution_log_path)
            if resume
            else ""
        )

        start_time = time.time()
        total_smells = 0

        for dirname in os.listdir(base_path):
            if dirname in {"output", "execution_log.txt"}:
                continue

            if resume and dirname <= last_project:
                continue

            project_path = os.path.join(base_path, dirname)

            if not os.path.isdir(project_path):
                continue

            print(f"Analyzing project '{dirname}' sequentially...")
            try:
                filenames = FileUtils.get_python_files(project_path)

                col = [
                    "filename",
                    "function_name",
                    "smell_name",
                    "line",
                    "description",
                    "additional_info",
                ]
                to_save = pd.DataFrame(columns=col)
                project_smells = 0

                for filename in filenames:
                    try:
                        result = self.inspector.inspect(filename)

                        smell_count = len(result)
                        project_smells += smell_count
                        if smell_count > 0:
                            print(
                                f"Found {smell_count} code "
                                f"smells in file: {filename}"
                            )
                        to_save = pd.concat(
                            [to_save, result], ignore_index=True
                        )
                    except (SyntaxError, FileNotFoundError) as e:
                        error_file = os.path.join(
                            self.output_path, "error.txt"
                        )
                        os.makedirs(self.output_path, exist_ok=True)
                        with open(error_file, "a") as f:
                            f.write(f"Error in file {filename}: {str(e)}\n")
                        print(f"Error analyzing file: {filename} - {str(e)}")
                        continue

                if not to_save.empty:
                    details_path = os.path.join(
                        self.output_path, "project_details"
                    )
                    os.makedirs(details_path, exist_ok=True)
                    detailed_file_path = os.path.join(
                        details_path, f"{dirname}_results.csv"
                    )
                    to_save.to_csv(detailed_file_path, index=False)
                    print(f"Detailed results saved to {detailed_file_path}")

                total_smells += project_smells
                print(
                    f"Project '{dirname}' analyzed successfully."
                    f"Code smells found: {project_smells}\n"
                )

                FileUtils.append_to_log(execution_log_path, dirname)

            except Exception as e:
                print(f"Error analyzing project '{dirname}': {str(e)}\n")

        print(
            "Sequential execution completed in "
            f"{time.time() - start_time:.2f} seconds."
        )
        print(f"Total code smells found in all projects: {total_smells}\n")

    def analyze_projects_parallel(self, base_path: str, max_workers: int):
        """
        Analyzes multiple projects in parallel.

        Parameters:
        - base_path (str): Directory containing projects to be analyzed.
        - max_workers (int): Maximum number of parallel threads.
        """
        execution_log_path = os.path.join(base_path, "execution_log.txt")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if not os.path.exists(execution_log_path):
            FileUtils.initialize_log(execution_log_path)

        start_time = time.time()
        total_smells = 0
        lock = threading.Lock()  # Thread-safe lock for logging

        def analyze_and_count_smells(dirname: str):
            nonlocal total_smells
            project_path = os.path.join(base_path, dirname)
            if dirname in {"output", "execution_log.txt"} or not os.path.isdir(
                project_path
            ):
                return

            print(f"Analyzing project '{dirname}' in parallel...")
            try:
                filenames = FileUtils.get_python_files(project_path)

                col = [
                    "filename",
                    "function_name",
                    "smell_name",
                    "line",
                    "description",
                    "additional_info",
                ]
                to_save = pd.DataFrame(columns=col)
                project_smells = 0

                for filename in filenames:
                    try:
                        result = self.inspector.inspect(filename)

                        smell_count = len(result)
                        project_smells += smell_count
                        if smell_count > 0:
                            print(
                                f"Found {smell_count} code "
                                f"smells in file: {filename}"
                            )
                        to_save = pd.concat(
                            [to_save, result], ignore_index=True
                        )
                    except (SyntaxError, FileNotFoundError) as e:
                        error_file = os.path.join(
                            self.output_path, "error.txt"
                        )
                        os.makedirs(self.output_path, exist_ok=True)
                        with open(error_file, "a") as f:
                            f.write(f"Error in file {filename}: {str(e)}\n")
                        print(f"Error analyzing file: {filename} - {str(e)}")
                        continue

                if not to_save.empty:
                    details_path = os.path.join(
                        self.output_path, "project_details"
                    )
                    os.makedirs(details_path, exist_ok=True)
                    detailed_file_path = os.path.join(
                        details_path, f"{dirname}_results.csv"
                    )
                    to_save.to_csv(detailed_file_path, index=False)
                    print(f"Detailed results saved to {detailed_file_path}")

                total_smells += project_smells

                # Thread-safe log update
                FileUtils.synchronized_append_to_log(
                    execution_log_path, dirname, lock
                )

            except Exception as e:
                print(f"Error analyzing project '{dirname}': {str(e)}\n")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for dirname in os.listdir(base_path):
                executor.submit(analyze_and_count_smells, dirname)

        print(
            "Parallel execution completed in "
            f"{time.time() - start_time:.2f} seconds."
        )
        print(f"Total code smells found in all projects: {total_smells}\n")

    def merge_all_results(self):
        """
        Merges all CSV result files from multiple
        projects into a single overview CSV in the root output folder.
        """
        FileUtils.merge_results(
            input_dir=os.path.join(self.output_path, "project_details"),
            output_dir=self.output_path,
        )
