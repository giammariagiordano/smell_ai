import os
import shutil
import pandas as pd


class FileUtils:
    """
    Handles file and directory-related operations.
    """

    @staticmethod
    def clean_directory(root_path: str, subfolder_name: str = "output") -> str:
        """
        Cleans or creates a specified subfolder within a root directory.

        Parameters:
        - root_path (str): Root directory where the subfolder will be created.
        - subfolder_name (str): Name of the subfolder to clean or create.

        Returns:
        - str: Path to the cleaned or created subfolder.
        """
        output_path = os.path.join(root_path, subfolder_name)

        if os.path.exists(output_path):
            for filename in os.listdir(output_path):
                file_path = os.path.join(output_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            os.makedirs(output_path)

        return output_path

    @staticmethod
    def get_python_files(path: str) -> list[str]:
        """
        Retrieves all Python files from the specified path.

        Parameters:
        - path (str): Path to search for Python files.

        Returns:
        - list[str]: List of Python file paths.
        """
        result = []
        if os.path.isfile(path) and path.endswith(".py"):
            return [path]

        for root, dirs, files in os.walk(path):
            if "venv" in dirs:
                dirs.remove("venv")
            if "lib" in dirs:
                dirs.remove("lib")
            for file in files:
                if file.endswith(".py"):
                    result.append(os.path.abspath(os.path.join(root, file)))
        return result

    @staticmethod
    def merge_results(input_dir: str, output_dir: str):
        """
        Merges analysis results from multiple projects into a single CSV.

        Parameters:
        - input_dir (str): Directory containing
          analysis results (project_name.csv files).
        - output_dir (str): Directory where the merged results will be saved.
        """
        dataframes = []
        print(f"Looking for CSV files in directory: {input_dir}")

        for subdir, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(subdir, file)
                    try:
                        df = pd.read_csv(file_path)
                        if not df.empty:
                            dataframes.append(df)
                        else:
                            print(f"Skipping empty CSV: {file_path}")
                    except Exception as e:
                        print(f"Failed to read {file_path}: {e}")

        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            os.makedirs(output_dir, exist_ok=True)
            combined_df.to_csv(
                os.path.join(output_dir, "overview.csv"), index=False
            )
            print(f"Merged results saved to {output_dir}/overview.csv")
        else:
            print("No valid CSV files found to merge.")

    @staticmethod
    def initialize_log(log_path: str):
        """
        Initializes an execution log file by overwriting its contents.

        Parameters:
        - log_path (str): Path to the log file to initialize.
        """
        with open(log_path, "w") as log_file:
            log_file.write("")
        print(f"Execution log initialized: {log_path}")

    @staticmethod
    def append_to_log(log_path: str, project_name: str):
        """
        Appends a project name to the execution log.

        Parameters:
        - log_path (str): Path to the log file.
        - project_name (str): Name of the project to append to the log.
        """
        with open(log_path, "a") as log_file:
            log_file.write(project_name + "\n")
        print(f"Appended to log: {project_name}")

    @staticmethod
    def get_last_logged_project(log_path: str) -> str:
        """
        Retrieves the last project name logged in the execution log.

        Parameters:
        - log_path (str): Path to the log file.

        Returns:
        - str: Name of the last logged project,
          or an empty string if the log is empty.
        """
        try:
            with open(log_path, "r") as log_file:
                lines = log_file.readlines()
                return lines[-1].strip() if lines else ""
        except FileNotFoundError:
            return ""

    @staticmethod
    def synchronized_append_to_log(log_path: str, project_name: str, lock):
        """
        Thread-safe method to append a project name to the execution log.

        Parameters:
        - log_path (str): Path to the log file.
        - project_name (str): Name of the project to append to the log.
        - lock: Threading lock to ensure synchronized writes.
        """
        with lock:
            with open(log_path, "a") as log_file:
                log_file.write(project_name + "\n")
            print(f"Thread-safe appended to log: {project_name}")
