import os
import pandas as pd

from cs_detector.code_extractor.libraries import extract_libraries
from cs_detector.detection_rules.Generic import *
from cs_detector.detection_rules.APISpecific import *
from cs_detector.code_extractor.models import load_model_dict, load_tensor_operations_dict
from cs_detector.code_extractor.dataframe_detector import load_dataframe_dict
def rule_check(node, libraries, filename, df_output,models,output_path):
    #create dictionaries and libraries useful for detection
    dataframe_path = os.path.abspath("../obj_dictionaries/dataframes.csv")
    df_dict = load_dataframe_dict(dataframe_path)
    tensor_dict = load_tensor_operations_dict()
    #start detection
    deterministic, deterministic_list = deterministic_algorithm_option_not_used(libraries, filename, node)
    merge, merge_list = merge_api_parameter_not_explicitly_set(libraries, filename, node,df_dict)
    columns_and_data, columns_and_data_list = columns_and_datatype_not_explicitly_set(libraries, filename, node,df_dict)
    empty, empty_list = empty_column_misinitialization(libraries, filename, node,df_dict)
    nan_equivalence, nan_equivalence_list = nan_equivalence_comparison_misused(libraries, filename, node)
    inplace, inplace_list = in_place_apis_misused(libraries, filename, node,df_dict)
    memory_not, memory_not_list = memory_not_freed(libraries, filename, node, models)
    chain, chain_list = Chain_Indexing(libraries, filename, node,df_dict)
    dataframe_conversion, dataframe_conversion_list = dataframe_conversion_api_misused(libraries, filename, node,df_dict)
    matrix_mul, matrix_mul_list = matrix_multiplication_api_misused(libraries, filename, node)
    gradients, gradients_list = gradients_not_cleared_before_backward_propagation(libraries, filename, node)
    tensor, tensor_list = tensor_array_not_used(libraries, filename, node)
    pytorch, pytorch_list = pytorch_call_method_misused(libraries, filename, node)
    unnecessary_iterations, unnecessary_iterations_list = unnecessary_iteration(libraries, filename, node, df_dict)
 #   hyper_parameters = hyperparameters_not_explicitly_set(libraries, filename, node,models)
    broadcasting_not_used,broadcasting_not_used_list = broadcasting_feature_not_used(libraries, filename, node,tensor_dict)
    if deterministic:
        df_output.loc[len(df_output)] = deterministic
        save_single_file(filename, deterministic_list,output_path)
    if merge:
        df_output.loc[len(df_output)] = merge
        save_single_file(filename, merge_list,output_path)
    if columns_and_data:
        df_output.loc[len(df_output)] = columns_and_data
        save_single_file(filename, columns_and_data_list,output_path)
    if empty:
        df_output.loc[len(df_output)] = empty
        save_single_file(filename, empty_list,output_path)
    if nan_equivalence:
        df_output.loc[len(df_output)] = nan_equivalence
        save_single_file(filename, nan_equivalence_list,output_path)
    if inplace:
        df_output.loc[len(df_output)] = inplace
        save_single_file(filename, inplace_list,output_path)
    if memory_not:
        df_output.loc[len(df_output)] = memory_not
        save_single_file(filename, memory_not_list,output_path)
    if chain:
        df_output.loc[len(df_output)] = chain
        save_single_file(filename, chain_list,output_path)
    if dataframe_conversion:
        df_output.loc[len(df_output)] = dataframe_conversion
        save_single_file(filename, dataframe_conversion_list,output_path)
    if matrix_mul:
        df_output.loc[len(df_output)] = matrix_mul
        save_single_file(filename, matrix_mul_list,output_path)
    if gradients:
        df_output.loc[len(df_output)] = gradients
        save_single_file(filename, gradients_list,output_path)
    if tensor:
        df_output.loc[len(df_output)] = tensor
        save_single_file(filename, tensor_list,output_path)
    if pytorch:
        df_output.loc[len(df_output)] = pytorch
        save_single_file(filename,pytorch_list, output_path)
    if unnecessary_iterations:
        df_output.loc[len(df_output)] = unnecessary_iterations
        save_single_file(filename, unnecessary_iterations_list,output_path)
    if broadcasting_not_used:
        df_output.loc[len(df_output)] = broadcasting_not_used
        save_single_file(filename, broadcasting_not_used_list,output_path)
 #   if hyper_parameters:
  #      df_output.loc[len(df_output)] = hyper_parameters
    return df_output
def save_single_file(filename, smell_list,output_path):
    cols = ["filename", "function_name", "smell_name", "line"]
    if os.path.exists(f'{output_path}/{smell_list[0]["smell_name"]}.csv'):
        to_save = pd.read_csv(f'{output_path}/{smell_list[0]["smell_name"]}.csv')
    else:
        to_save = pd.DataFrame(columns=cols)
    for smell in smell_list:
        to_save.loc[len(to_save)] = smell
    smell_name = smell_list[0]['smell_name']
    to_save.to_csv(f'{output_path}/{smell_name}.csv', index=False)
def inspect(filename, output_path):
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
    file_path = os.path.join(filename)
    try:
        with open(file_path, "rb") as file:
            source = file.read()
    except FileNotFoundError as e:
        message = f"Error in file {filename}: {e}"
        raise FileNotFoundError(message)
    try:
        tree = ast.parse(source)
        libraries = extract_libraries(tree)
        models = load_model_dict()
        # Visita i nodi dell'albero dell'AST alla ricerca di funzioni
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                rule_check(node, libraries, filename, to_save,models,output_path)
    except SyntaxError as e:
        message = f"Error in file {filename}: {e}"
        raise SyntaxError(message)
    return to_save
