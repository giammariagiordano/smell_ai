import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
from components import detector
import argparse


def merge_results(input_dir="../output", output_dir="../general_output"):
    dataframes = []
    for subdir, dirs, files in os.walk(input_dir):
        if "to_save.csv" in files:
            df = pd.read_csv(os.path.join(subdir, "to_save.csv"))
            if len(df) > 0:
                dataframes.append(df)

    if dataframes:
        combined_df = pd.concat(dataframes)
        #rimuovi tutti le linee contenti filename,function_name,smell,name_smell,message tranne la prima
        combined_df = combined_df[combined_df["filename"] != "filename"]
        combined_df = combined_df.reset_index()


        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        combined_df.to_csv(os.path.join(output_dir, "overview_output.csv"), index=False)
    else:
        print("Error.")


def find_python_files(url):
    try:
        # Estraiamo il path della directory radice del progetto e lo salaviamo in 'root'
        root = os.path.dirname(os.path.abspath(url))
        py_files = []
        # Attraversiamo ricorsivamente tutte le directory al di sotto della root
        for dirpath, _, filenames in os.walk(root):
            # Per ogni file all'interno della directory
            for f in filenames:
                # Se il file ha estensione .py, aggiungiamo il suo path assoluto alla lista 'py_files'
                if f.endswith('.py'):
                    py_files.append(os.path.join(dirpath, f))
        return py_files
    except Exception as e:
        print(f"Errore durante la ricerca dei file Python: {e}")


def get_python_files(path):
    result = []
    if os.path.isfile(path):
        if path.endswith(".py"):
            result.append(path)
            return result
    for root, dirs, files in os.walk(path):
        if "venv" in dirs:
            dirs.remove("venv")
        if "lib" in dirs:
            dirs.remove("lib")
        for file in files:
            if file.endswith(".py"):
                result.append(os.path.abspath(os.path.join(root, file)))
    return result


def analyze_project(project_path, output_path="."):
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    filenames = get_python_files(project_path)

    for filename in filenames:
        if "tests/" not in filename:  # ignore test files
            try:
                result = detector.inspect(filename, output_path)
                to_save = to_save.merge(result, how='outer')
            except SyntaxError as e:
                message = e.msg
                error_path = output_path
                if not os.path.exists(error_path):
                    os.makedirs(error_path)
                with open(f"{error_path}/error.txt", "a") as error_file:
                    error_file.write(message)
                continue
            except FileNotFoundError as e:
                message = e
                error_path = output_path
                if not os.path.exists(error_path):
                    os.makedirs(error_path)
                with open(f"{error_path}/error.txt", "a") as error_file:
                    error_file.write(str(message))
                continue

    to_save.to_csv(output_path + "/to_save.csv", index=False, mode='a')


def projects_analysis(base_path='../input/projects', output_path='../output/projects_analysis',resume=False):
    start = time.time()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    dirpath = os.listdir(base_path)
    if not os.path.exists("../config/execution_log.txt"):
        #get abs path of execution_log.txt
        execution_log_path = os.path.abspath("../config/execution_log.txt")
        print("Path:"+execution_log_path)
        open("../config/execution_log.txt", "w").close()
        resume = False
    execution_log = open("../config/execution_log.txt", "a")
    #get last project analyzed in execution_log.txt
    if resume:
        with open("../config/execution_log.txt", "r") as f:
            last_project = f.readlines()[-1]
    for dirname in dirpath:
        if resume:
            if dirname <= last_project:
                continue
        new_path = os.path.join(base_path, dirname)
        if not os.path.exists(f"{output_path}/{dirname}"):
            os.makedirs(f"{output_path}/{dirname}")
        print(f"Analyzing {dirname}...")

        analyze_project(new_path, f"{output_path}/{dirname}")
        print(f"{dirname} analyzed successfully.")
        execution_log.write(dirname + "\n")
    end = time.time()
    print(f"Sequential Exec Time completed in: {end - start}")


def parallel_projects_analysis(base_path='../input/projects', output_path='../output/projects_analysis', max_workers=5,resume=False):
    start = time.time()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        dirpath = os.listdir(base_path)
        for dirname in dirpath:
            new_path = os.path.join(base_path, dirname)
            if not os.path.exists(f"{output_path}/{dirname}"):
                os.makedirs(f"{output_path}/{dirname}")
            executor.submit(analyze_project, new_path, f"{output_path}/{dirname}")
    end = time.time()
    print(f"Parallel Exec Time completed in: {end - start}")


def clean(output_path="../output/projects_analysis"):
    # check os windows or linux

    if os.name == "nt":
        clean_win_path = output_path.replace("/", "\\")
        if os.path.exists(clean_win_path):
            os.system(f"rmdir /s /q {clean_win_path}")

    else:
        if os.path.exists(output_path):
            os.system(f"rm -r {output_path}")



def main(args):
    print(args.input)
    print(args.output)

    if args.input is None or args.output is None:
        print("Please specify input and output folders")
        exit(0)
    resume = True

    multiple = args.multiple
    if multiple:
        if not args.resume:
            resume = False
            clean(args.output)
        if args.parallel:
            parallel_projects_analysis(args.input, args.output, args.max_workers,resume)
        else:
            if not os.path.exists(f"{args.output}"):
                os.makedirs(f"{args.output}")
            projects_analysis(args.input, args.output,resume)
    else:

        analyze_project(args.input, args.output)
    merge_results(args.output, args.output+"/overview")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code Smile is a tool for detecting AI-specific code smells "
                                                 "for Python projects")
    parser.add_argument("--input", type=str, help="Path to the input folder")
    parser.add_argument("--output", type=str, help="Path to the output folder")
    parser.add_argument("--max_workers", type=int, default=5,help="Number of workers for parallel execution")
    parser.add_argument("--parallel",default=False, type=bool, help="Enable parallel execution")
    parser.add_argument("--resume", default=False, type=bool, help="Continue previous execution")
    parser.add_argument("--multiple", default=False, type=bool, help="Enable multiple projects analysis")
    args = parser.parse_args()
    main(args)



