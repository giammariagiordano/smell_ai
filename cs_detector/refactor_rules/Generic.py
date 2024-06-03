import os
import astunparse
import ast
import re
from ..code_extractor.models import check_model_method
from ..code_extractor.libraries import get_library_of_node, extract_library_name, extract_library_as_name

from ..code_extractor.dataframe_detector import dataframe_check
from ..code_extractor.variables import search_variable_definition

test_libraries = ["pytest", "robot", "unittest", "doctest", "nose2", "testify", "pytest-cov", "pytest-xdist"]

def get_lines_of_code(node):
    function_name = node.name

    function_body = ast.unparse(node.body).strip()
    lines = function_body.split('\n')
    return function_name, lines


def filePatch(filename, source, lineno, oldCode, newCode):
    #Aprire file, leggere riga lineno, con una funzione trova l'inizio del vecchio codice e ci sostituisce il nuovo
    #print("dentro filePatch")
    
    file_path = os.path.join(filename)
    out = open(file_path, 'w', encoding="utf-8")

    line = source[lineno - 1]
    line = line.replace(oldCode, newCode)
    source[lineno - 1] = line             
    
    out.write(''.join(source))
    out.close()

def R_empty_column_misinitialization(source, libraries, filename, fun_node, df_dict):
    if [x for x in libraries if x in test_libraries]:
        return [], []
    smell_instance_list = []
    # this is the list of values that are considered as smelly empty values
    empty_values = ['0', "''", '""']
    function_name, lines = get_lines_of_code(fun_node)
    if [x for x in libraries if 'pandas' in x]:
        # get functions call of read_csv
        read_csv = []
        variables = []
        number_of_apply = 0
        # get all defined variables that are dataframes
        variables = dataframe_check(fun_node, libraries, df_dict)
        # for each assignment of a variable
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Assign):
                target = node.targets[0]
                # check if the variable is a dataframe
                if isinstance(target, ast.Subscript) and hasattr(target.value, 'id'):
                    #print("SUPERATO CONTROLLO")
                #if hasattr(node.targets[0], 'id'):
                    #print(ast.dump(node))
                    if target.value.id in variables:
                    #if node.targets[0].id in variables:
                        # check if the line is an assignment of a column of the dataframe
                        #print("Trovata variabile in dataframe")
                        #print(ast.dump(node.targets[0]))
                        #if isinstance(node.targets[0], ast.Subscript):
                            # select a line where uses to define a column df.[*] = *
                        #pattern = re.escape(target.value.id) + r'\[.*\]'
                        pattern = target.value.id + '\[.*\]'
                        #print("Trovata colonna appropriata per lo smell")
                        #print(node.lineno)
                            # check if the line is an assignment of the value is 0 or ''
                        if re.match(pattern, ast.unparse(node).strip()):
                            if ast.unparse(node).strip().split('=')[1].strip() in empty_values:
                                new_smell = {'filename': filename, 'function_name': function_name,
                                                    'smell_name': 'empty_column_misinitialization',
                                                    'line': node.lineno}
                                smell_instance_list.append(new_smell)
                                number_of_apply += 1
                                
                                #print(ast.dump(node))
                                oldCode = astunparse.unparse(node.value).strip()
                                #print(oldCode)
                                #print(astunparse.unparse(node.left).strip())
                                #node.targets[1].value = 'np.nan()'
                                #print(ast.dump(node))
                                newCode = 'np.nan()'
                                #print(newCode)
                                
                                filePatch(filename, source, node.lineno, oldCode, newCode)

                            

        if number_of_apply > 0:
            message = "If they use zeros or empty strings to initialize a new empty column in Pandas" \
                      "the ability to use methods such as .isnull() or .notnull() is retained." \
                      "Use NaN value (e.g. np.nan) if a new empty column in a DataFrame is needed. Do not use “filler values” such as zeros or empty strings."
            name_smell = "empty_column_misinitialization"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []


def R_nan_equivalence_comparison_misused(source, libraries, filename, fun_node):
    library_name = ""
    if [x for x in libraries if x in test_libraries]:
        return [], []
    smell_instance_list = []
    if [x for x in libraries if 'numpy' in x]:
        for x in libraries:
            if 'numpy' in x:
                library_name = extract_library_as_name(x)
        function_name = fun_node.name
        number_of_nan_equivalences = 0
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Compare):
                nan_equivalence = False
                if hasattr(node.left, "value"):
                    if hasattr(node.left.value, 'id'):
                        if isinstance(node.left,
                                      ast.Attribute) and node.left.attr == 'nan' and node.left.value.id == library_name:
                            nan_equivalence = True
                        for expr in node.comparators:
                            if isinstance(expr, ast.Attribute) and expr.attr == 'nan' and expr.value.id == library_name:
                                nan_equivalence = True
                        if nan_equivalence:
                            new_smell = {'filename': filename, 'function_name': function_name,
                                            'smell_name': 'nan_equivalence_comparison_misused',
                                            'line': node.lineno}
                            smell_instance_list.append(new_smell)
                            number_of_nan_equivalences += 1
                            
                            compName = astunparse.unparse(node.left).strip()
                            
                            #print(ast.dump(node))
                            oldCode = astunparse.unparse(node).strip()[1:-1]
                            #print(oldCode)
                            #print(astunparse.unparse(node.left).strip())
                            #node.func.attr = 'net'
                            #print(ast.dump(node))
                            newCode = "np.isnan(" + compName + ")"
                            #print(newCode)
                            
                            filePatch(filename, source, node.lineno, oldCode, newCode)
                            
        if number_of_nan_equivalences > 0:
            message = "NaN equivalence comparison misused"
            name_smell = "nan_equivalence_comparison_misused"
            to_return = [filename, function_name, number_of_nan_equivalences, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []
