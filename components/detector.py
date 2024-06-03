import os

import pandas as pd

from cs_detector.code_extractor.dataframe_detector import load_dataframe_dict
from cs_detector.code_extractor.libraries import extract_libraries
from cs_detector.code_extractor.models import (load_model_dict,
                                               load_tensor_operations_dict)
from cs_detector.detection_rules.APISpecific import *
from cs_detector.detection_rules.Generic import *
from cs_detector.refactor_rules.APISpecific import (
    R_dataframe_conversion_api_misused,
    R_gradients_not_cleared_before_backward_propagation,
    R_matrix_multiplication_api_misused, R_pytorch_call_method_misused,
    R_tensor_array_not_used)
from cs_detector.refactor_rules.Generic import (
    R_empty_column_misinitialization, R_nan_equivalence_comparison_misused)


def rule_check(source, node, libraries, filename, df_output,models,output_path, refactor):
        
    #print("Entrato in rule check")    
    
    #create dictionaries and libraries useful for detection
    dataframe_path = os.path.abspath("../obj_dictionaries/dataframes.csv")
    
    #print("Ottenuto dataframe")
    
    #print(dataframe_path)
    
    df_dict = load_dataframe_dict(dataframe_path)
    
    #print("Caricato dataframe")
    
    tensor_dict = load_tensor_operations_dict()
    line_offset = 0 #indica spostamento di riga dovuto ad aggiunta da refactor precedente
    #print("Prima di detection")
    
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
        
        #if refactor: //Qui bisogna mettere funzione per il refactoring
        
       # print("PRIMA REFACTOR")
        
        if refactor:
            if line_offset != 0:
                ast.increment_lineno(node, line_offset)
            R_empty, R_empty_list = R_empty_column_misinitialization(source, libraries, filename, node, df_dict)
            df_output.loc[len(df_output)] = R_empty
            save_refactor_single_file(filename, R_empty_list,output_path)
        #print("DOPO REFACTOR")
        
        df_output.loc[len(df_output)] = empty
        save_single_file(filename, empty_list,output_path)
    if nan_equivalence:
        
        if refactor: #//Qui bisogna mettere funzione per il refactoring
            if line_offset != 0:
                ast.increment_lineno(node, line_offset)
            R_nan_equivalence, R_nan_equivalence_list = R_nan_equivalence_comparison_misused(source, libraries, filename, node)
            df_output.loc[len(df_output)] = R_nan_equivalence
            save_refactor_single_file(filename, R_nan_equivalence_list,output_path)

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
        
        if refactor: #//Qui bisogna mettere funzione per il refactoring
            if line_offset != 0:
                ast.increment_lineno(node, line_offset)
            R_dataframe_conversion, R_dataframe_conversion_list = R_dataframe_conversion_api_misused(source, libraries, filename, node, df_dict)
            df_output.loc[len(df_output)] = R_dataframe_conversion
            save_refactor_single_file(filename, R_dataframe_conversion_list,output_path)    
        df_output.loc[len(df_output)] = dataframe_conversion
        save_single_file(filename, dataframe_conversion_list,output_path)
    if matrix_mul:
        
        if refactor: #//Qui bisogna mettere funzione per il refactoring
            if line_offset != 0:
                ast.increment_lineno(node, line_offset)
            R_matrix_mul, R_matrix_mul_list = R_matrix_multiplication_api_misused(source, libraries, filename, node)
            df_output.loc[len(df_output)] = R_matrix_mul
            save_refactor_single_file(filename, R_matrix_mul_list,output_path)
        
        df_output.loc[len(df_output)] = matrix_mul
        save_single_file(filename, matrix_mul_list,output_path)
    if gradients:
        
        if refactor: #//Qui bisogna mettere funzione per il refactoring
            R_gradients, R_gradients_list = R_gradients_not_cleared_before_backward_propagation(source, libraries, filename, node)
            line_offset = line_offset + 1
            #print("AUMENTATO IN GRADIENTS")
            df_output.loc[len(df_output)] = R_gradients
            save_refactor_single_file(filename, R_gradients_list,output_path)

        df_output.loc[len(df_output)] = gradients
        save_single_file(filename, gradients_list,output_path)
    if tensor:
        
        if refactor: #Qui bisogna mettere funzione per il refactoring
            if line_offset != 0:
                #print("AUMENTATO")
                ast.increment_lineno(node, line_offset)
            R_tensor, R_tensor_list = R_tensor_array_not_used(source, libraries, filename, node)
            df_output.loc[len(df_output)] = R_tensor
            save_refactor_single_file(filename, R_tensor_list,output_path)
            #print("LINENO" + str(node.lineno))
        
        df_output.loc[len(df_output)] = tensor
        save_single_file(filename, tensor_list,output_path)
    if pytorch:
        
        if refactor: #//Qui bisogna mettere funzione per il refactoring
            if line_offset != 0:
                ast.increment_lineno(node, line_offset)
            R_pytorch, R_pytorch_list = R_pytorch_call_method_misused(source, libraries, filename, node)
            df_output.loc[len(df_output)] = R_pytorch
            save_refactor_single_file(filename, R_pytorch_list,output_path)

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
  
    #print("RESTITUISCO OUTPUT")

    return df_output, line_offset
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
def inspect(filename, output_path, refactor):
    
    #print("Entrato in inspect")
    
    col = ["filename", "function_name", "smell", "name_smell", "message"]
    to_save = pd.DataFrame(columns=col)
        
    #print("Prima di file path")    
    
    file_path = os.path.join(filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source = file.readlines()
    except FileNotFoundError as e:
        message = f"Error in file {filename}: {e}"
        raise FileNotFoundError(message)
    try:
        
        #print("Prima di tree")
        
        sourceJoined = ''.join(source)
        tree = ast.parse(sourceJoined)
        libraries = extract_libraries(tree)
        models = load_model_dict()
        offset = 0
        # Visita i nodi dell'albero dell'AST alla ricerca di funzioni
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                ast.increment_lineno(node, offset)
                df, temp_offset = rule_check(source, node, libraries, filename, to_save,models,output_path, refactor) #Modifica, gli ho passato il file
                if temp_offset != 0:
                    offset = offset + temp_offset
                
    except SyntaxError as e:
        message = f"Error in file {filename}: {e}"
        raise SyntaxError(message)
    return to_save
def save_refactor_single_file(filename, smell_list,output_path):
    cols = ["filename", "function_name", "smell_name", "line"]
    if os.path.exists(f'{output_path}/ R_{smell_list[0]["smell_name"]}.csv'):
        to_save = pd.read_csv(f'{output_path}/ R_{smell_list[0]["smell_name"]}.csv')
    else:
        to_save = pd.DataFrame(columns=cols)
    for smell in smell_list:
        to_save.loc[len(to_save)] = smell
    smell_name = "R_" + smell_list[0]['smell_name']
    to_save.to_csv(f'{output_path}/Ref/{smell_name}.csv', index=False)
