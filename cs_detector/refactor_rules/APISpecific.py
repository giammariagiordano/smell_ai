import ast
import astunparse
import re
import os

from cs_detector.code_extractor.dataframe_detector import dataframe_check
from cs_detector.code_extractor.variables import search_variable_definition
from cs_detector.code_extractor.libraries import extract_library_as_name

test_libraries = ["pytest", "robot", "unittest", "doctest", "nose2", "testify", "pytest-cov", "pytest-xdist"]

def filePatch(filename, source, lineno, oldCode, newCode):
    #Aprire file, leggere riga lineno, con una funzione trova l'inizio del vecchio codice e ci sostituisce il nuovo
    #print("dentro filePatch")
    
    file_path = os.path.join(filename)
    out = open(file_path, 'w')

    line = source[lineno - 1]
    line = line.replace(oldCode, newCode)
    source[lineno - 1] = line             
    
    out.write(''.join(source))
    out.close()
    
def addLine(filename, source, lineno, newCode):
    file_path = os.path.join(filename)
    out = open(file_path, 'w')

    line = source[lineno]
    #print("RIGA CHE VOGLIO COPIARE:" + line)
        
    line = line.replace(line.strip(), newCode) 
    #print("NUOVA RIGA: " + line)     
    source.insert(lineno, line)
        
    out.write(''.join(source))
    out.close()
            

def R_dataframe_conversion_api_misused(source, libraries, filename, fun_node, df_dict):
    if [x for x in libraries if 'pandas' in x]:
        function_name = fun_node.name
        variables = dataframe_check(fun_node, libraries, df_dict)
        number_of_apply = 0
        smell_instance_list = []
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Attribute):
                if hasattr(node, 'value'):
                    if hasattr(node, 'attr'):
                        if node.attr == 'values':
                            if hasattr(node, 'value'):
                                if hasattr(node.value, 'id'):
                                    if node.value.id in variables:
                                        
                                        #Confermato smell, lo aggiunge a lista
                                        new_smell = {'filename': filename, 'function_name': function_name,
                                                     'smell_name': 'dataframe_conversion_api_misused',
                                                     'line': node.lineno}
                                        smell_instance_list.append(new_smell)
                                        number_of_apply += 1
                                        
                                        #Dopo averlo confermato, se il flag di refactor è attivo, fa refactoring ed aggiunge a lista di refactor
                                        
                                        #Use df.to_numpy() in Pandas instead of df.values() for transform a DataFrame to a NumPy array.
                                       # print(ast.dump(node))
                                        oldCode = astunparse.unparse(node).strip()
                                       # print(oldCode)
                                        node.attr = 'to_numpy'
                                        #print(ast.dump(node))
                                        newCode = astunparse.unparse(node).strip() + '()'
                                        #print(newCode)
                                        
                                        filePatch(filename, source, node.lineno, oldCode, newCode)
                                        
        if number_of_apply > 0:
            message = "Please consider to use numpy instead values to convert dataframe. The function 'values' is deprecated." \
                  "The value return of this function is unclear."
            name_smell = "dataframe_conversion_api_misused"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []



def R_matrix_multiplication_api_misused(source, libraries, filename, fun_node):
    number_of_apply = 0
    library_name = ""
    function_name = ""
    smell_instance_list = []
    if [x for x in libraries if x in test_libraries]:
        return [], []
    if [x for x in libraries if 'numpy' in x]:
        for x in libraries:
            if 'numpy' in x:
                library_name = extract_library_as_name(x)
                function_name = fun_node.name
        if library_name == "":
            return [], []
        for node in ast.walk(fun_node):
            # search for dot function usages
            if isinstance(node, ast.Call):
                if hasattr(node, 'func'):
                    if hasattr(node.func, 'attr'):
                        if hasattr(node.func, 'value'):
                            if hasattr(node.func.value, 'id'):
                                if node.func.attr == 'dot' and node.func.value.id == library_name:
                                    # if dot function used with constant matrices, increase number of apply
                                    if hasattr(node, 'args'):
                                        if len(node.args) > 1:
                                            arguments = []
                                            matrix_multiplication = False
                                            for arg in node.args:
                                                # check if each argument is a list
                                                if isinstance(arg, ast.List):

                                                    # check if each list contains a list, so it is a matrix
                                                    for el in arg.elts:

                                                        if isinstance(el, ast.List):
                                                            matrix_multiplication = True

                                                else:
                                                    if isinstance(arg, ast.Name):
                                                        # in this case we have to extract variables and see if it is a matrix
                                                        arguments.append(arg.id)
                                            if matrix_multiplication:
                                                new_smell = {'filename': filename, 'function_name': function_name,
                                                                'smell_name': 'matrix_multiplication_api_misused',
                                                                'line': node.lineno}
                                                smell_instance_list.append(new_smell)
                                                number_of_apply += 1
                                                
                                               # print(ast.dump(node))
                                                oldCode = astunparse.unparse(node).strip()
                                                #print(oldCode)
                                                node.func.attr = 'matmul'
                                                #print(ast.dump(node))
                                                newCode = astunparse.unparse(node).strip()
                                                #print(newCode)
                                        
                                                filePatch(filename, source, node.lineno, oldCode, newCode)

                                            else:
                                                for arg in arguments:
                                                    node_def = search_variable_definition(arg, fun_node, node)
                                                    if node_def is not None:
                                                        constant = node_def.value
                                                        if isinstance(constant, ast.List):
                                                            for el in constant.elts:
                                                                if isinstance(el, ast.List):
                                                                    matrix_multiplication = True
                                                if matrix_multiplication:
                                                    new_smell = {'filename': filename, 'function_name': function_name,
                                                                    'smell_name': 'matrix_multiplication_api_misused',
                                                                    'line': node.lineno}
                                                    smell_instance_list.append(new_smell)
                                                    number_of_apply += 1
                                                    
                                                    #print(ast.dump(node))
                                                    oldCode = astunparse.unparse(node).strip()
                                                    #print(oldCode)
                                                    node.func.attr = 'matmul'
                                                    #print(ast.dump(node))
                                                    newCode = astunparse.unparse(node).strip()
                                                    #print(newCode)
                                        
                                                    filePatch(filename, source, node.lineno, oldCode, newCode)

        if number_of_apply > 0:
            message = "Please consider to use np.matmul to multiply matrix. The function dot() not return a scalar value, " \
                      "but a matrix."
            name_smell = "matrix_multiplication_api_misused"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []


def R_gradients_not_cleared_before_backward_propagation(source, libraries, filename, fun_node):
    library_name = ""
    if [x for x in libraries if x in test_libraries]:
        return [], []
    if [x for x in libraries if 'torch' in x]:
        for x in libraries:
            if 'torch' in x:
                library_name = extract_library_as_name(x)
        function_name = fun_node.name
        number_of_apply = 0
        smell_instance_list = []
        for node in ast.walk(fun_node):
            if isinstance(node, ast.For) or isinstance(node,ast.While):
                zero_grad_called = False
                backwardFound = False
                for node2 in ast.walk(node):
                    if isinstance(node2, ast.Call):
                        if hasattr(node2, 'func'):
                            if hasattr(node2.func, 'attr'):
                                if node2.func.attr == 'zero_grad':
                                    zero_grad_called = True
                                if node2.func.attr == 'backward':
                                    if not zero_grad_called:
                                        new_smell = {'filename': filename, 'function_name': function_name,
                                                        'smell_name': 'gradients_not_cleared_before_backward_propagation',
                                                        'line': node2.lineno}
                                        smell_instance_list.append(new_smell)
                                        number_of_apply += 1
                                        backwardFound = True
                                        backwardLineNo = node2.lineno
                                        
                                if node2.func.attr == "step":
                                    if(backwardFound):
                                        newNode = node2
                                        newNode.func.attr = 'zero_grad'
                                        
                                        #optName = node2.func.value.id
                                        addLine(filename, source, backwardLineNo - 1, astunparse.unparse(newNode).strip())
        if number_of_apply > 0:
            message = "Please consider to use zero_grad() before backward()."
            name_smell = "gradients_not_cleared_before_backward_propagation"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []



def R_tensor_array_not_used(source, libraries, filename, fun_node):
    library_name = ""
    if [x for x in libraries if x in test_libraries]:
        return [], []
    if [x for x in libraries if 'tensorflow' in x]:
        function_name = fun_node.name
        function_body = ast.unparse(fun_node.body).strip()
        for x in libraries:
            if 'tensorflow' in x:
                library_name = extract_library_as_name(x)
        number_of_apply = 0
        smell_instance_list = []
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if hasattr(node.func.value, "id"):
                        if node.func.attr == "constant" and node.func.value.id == library_name:
                            if len(node.args) >= 1:
                                parameter = ast.unparse(node.args[0])
                                for arg_node in node.args:
                                    if isinstance(arg_node, ast.List):
                                        new_smell = {'filename': filename, 'function_name': function_name,
                                                        'smell_name': 'tensor_array_not_used',
                                                        'line': node.lineno}
                                        smell_instance_list.append(new_smell)
                                        number_of_apply += 1
                                        
                                        #print(ast.dump(node))
                                        oldCode = astunparse.unparse(node).strip()
                                        #print(oldCode)
                                        node.func.attr = 'TensorArray()'
                                        #print(ast.dump(node))
                                        newCode = astunparse.unparse(node).strip()
                                        #print(newCode)
                                        
                                        filePatch(filename, source, node.lineno, oldCode, newCode)
        if number_of_apply > 0:
            message = "If the developer initializes an array using tf.constant() and tries to assign a new value to " \
                      "it in the loop to keep it growing, the code will run into an error." \
                      "Using tf.TensorArray() for growing array in the loop is a better solution for this kind of " \
                      "problem in TensorFlow 2."
            name_smell = "tensor_array_not_used"
            to_return = [filename, function_name, number_of_apply, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []



def R_pytorch_call_method_misused(source, libraries, filename, fun_node):
    if [x for x in libraries if x in test_libraries]:
        return [], []
    if [x for x in libraries if 'torch' in x]:
        function_name = fun_node.name
        function_body = ast.unparse(fun_node.body).strip()
        lines = function_body.split('\n')
        number_of_forward = 0
        smell_instance_list = []
        for node in ast.walk(fun_node):
            if isinstance(node, ast.Call):
                if hasattr(node, 'func'):
                    if hasattr(node.func, 'attr') and hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
                        if node.func.attr == 'forward' and node.func.value.id == 'self':
                            new_smell = {'filename': filename, 'function_name': function_name,
                                            'smell_name': 'pytorch_call_method_misused',
                                            'line': node.lineno}
                            smell_instance_list.append(new_smell)
                            number_of_forward += 1
                            
                            #print(ast.dump(node))
                            oldCode = astunparse.unparse(node).strip()
                            #print(oldCode)
                            node.func.attr = 'net'
                            #print(ast.dump(node))
                            newCode = astunparse.unparse(node).strip()
                            #print(newCode)
                            
                            filePatch(filename, source, node.lineno, oldCode, newCode)

                            
        if number_of_forward > 0:
            message = "is recommended to use self.net()"
            name_smell = "pytorch_call_method_misused"
            to_return = [filename, function_name, number_of_forward, name_smell, message]
            return to_return, smell_instance_list
        return [], []
    return [], []
