import ast
import re
from ..code_extractor.models import check_model_method
from ..code_extractor.libraries import get_library_of_node, extract_library_name, extract_library_as_name

from ..code_extractor.dataframe_detector import dataframe_check
from ..code_extractor.variables import search_variable_definition

test_libraries = ["pytest", "robot", "unittest", "doctest", "nose2", "testify", "pytest-cov", "pytest-xdist"]

def R_empty_column_misinitialization(libraries, filename, fun_node, df_dict):
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
                # check if the variable is a dataframe
                if hasattr(node.targets[0], 'id'):
                    if node.targets[0].id in variables:
                        # check if the line is an assignment of a column of the dataframe
                        if hasattr(node.targets[0], 'slice'):
                            
                            print("CONTROLLO ASSEGNAMENTO: " + node.targets[0])
                            
                            # select a line where uses to define a column df.[*] = *
                            pattern = node.targets[0].id + '\[.*\]'
                            # check if the line is an assignment of the value is 0 or ''
                            if re.match(pattern, lines[node.lineno - 1]):
                                if lines[node.lineno - 1].split('=')[1].strip() in empty_values:
                                    new_smell = {'filename': filename, 'function_name': function_name,
                                                    'smell_name': 'empty_column_misinitialization',
                                                    'line': node.lineno}
                                    smell_instance_list.append(new_smell)
                                    number_of_apply += 1
                                    
                                    #Qui faccio il refactor
                                    

        if number_of_apply > 0:
            message = "If they use zeros or empty strings to initialize a new empty column in Pandas" \
                      "the ability to use methods such as .isnull() or .notnull() is retained." \
                      "Use NaN value (e.g. np.nan) if a new empty column in a DataFrame is needed. Do not use “filler values” such as zeros or empty strings."
            name_smell = "empty_column_misinitialization"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []


def nan_equivalence_comparison_misused(libraries, filename, fun_node):
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
        if number_of_nan_equivalences > 0:
            message = "NaN equivalence comparison misused"
            name_smell = "nan_equivalence_comparison_misused"
            to_return = [filename, function_name, number_of_nan_equivalences, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []
