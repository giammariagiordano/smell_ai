import shutil
from controller import analyzer
from components import detector
from cs_detector.detection_rules import Generic, APISpecific
from cs_detector.refactor_rules import Generic, APISpecific

import os, pytest, argparse, pandas

@pytest.fixture 
def parse():
    parser = argparse.ArgumentParser(description="Code Smile is a tool for detecting AI-specific code smells for Python projects")
    parser.add_argument("--input", type=str, help="Path to the input folder")
    parser.add_argument("--output", type=str, help="Path to the output folder")
    parser.add_argument("--max_workers", type=int, default=5,help="Number of workers for parallel execution")
    parser.add_argument("--parallel",default=False, type=bool, help="Enable parallel execution")
    parser.add_argument("--resume", default=False, type=bool, help="Continue previous execution")
    parser.add_argument("--multiple", default=False, type=bool, help="Enable multiple projects analysis")
    parser.add_argument("--refactor", action = "store_true", help="Enable refactoring of found smells")
    return parser

class TestCR3:
        
    def test_RA_1(self, parse):
        args = parse.parse_args(["--input", "C:/Users/Utente/CodeSmile/smell_ai/input/projects", "--output",  "C:/Users/Utente/CodeSmile/smell_ai/output/projects_analysis", "--refactor"])
        assert args.refactor is True
        
    def test_RM_1(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "tmpProject1"
        tempDir.mkdir()
        tempDir2 = tmp_path / "tmpProject2"
        tempDir2.mkdir()
        tempFile1 = tempDir / "Code_Smell_Examples.py"
        tempFile2 = tempDir2 / "Single_Smell_Example.py"
        originalFile1 = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tmp_path), "--output", str(tempOutput), "--refactor", "--multiple", "True"])
        analyzer.main(args)
        
        if(os.path.exists(tempOutput / "tmpProject1" / "Ref/R_to_save.csv") & os.path.exists(tempOutput / "tmpProject2" / "Ref/R_to_save.csv")):
            if(os.path.exists(tempOutput / "R_overview"/ "overview_output.csv")):
                assert True    
            else:
                assert False
    
    def test_RM_2(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "tmpProject"
        tempDir.mkdir()
        tempFile = tempDir / "Code_Smell_Examples.py"
        originalFile = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        assert os.path.exists(str(tempOutput) + "/Ref/R_to_save.csv")
    
    def test_RC_1(self, parse, tmp_path):
        
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "tmpProject"
        tempDir.mkdir()
        tempFile = tempDir / "Code_Smell_Examples.py"
        originalFile = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        if(os.path.exists(str(tempOutput) + "/Ref/R_to_save.csv")):
            #Apri il csv, controlla che smell presenti corrispondano
            df = pandas.read_csv(str(tempOutput) + "/Ref/R_to_save.csv")
            oracle = {'filename': {0: str(tempFile), 1: str(tempFile), 2: str(tempFile), 3: str(tempFile), 4: str(tempFile), 5: str(tempFile), 6: str(tempFile), 7: str(tempFile), 8: str(tempFile)}, 
                      'function_name': {0: "dataframe_conversion_api_misused_example", 1: "empty_example", 2: "empty_example", 3: "gradient_not_cleared_before_backward_propagation" , 4: "matrix_mul_example", 5: "nan_equivalence_example2" , 6: "pytorch_call_method_misused_example2", 7: "pytorch_call_method_misused_example2", 8: "tensor_example"},
                      'smell_name': {0: "dataframe_conversion_api_misused", 1: "empty_column_misinitialization", 2: "empty_column_misinitialization", 3: "gradients_not_cleared_before_backward_propagation" , 4: "matrix_multiplication_api_misused", 5: "nan_equivalence_comparison_misused" , 6: "pytorch_call_method_misused", 7: "pytorch_call_method_misused", 8: "tensor_array_not_used"},
                      'line': {0: 197, 1: 130, 2: 131, 3: 147 , 4: 187, 5: 125 , 6: 167, 7: 167, 8: 174}
                      }
            assert df.to_dict() == oracle
        else:
            assert False
        
    def test_RS_1(self, parse, tmp_path):  
           
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "tmpProject"
        tempDir.mkdir()
        tempFile1 = tempDir / "Code_Smell_Examples.py"
        tempFile2 = tempDir / "Single_Smell_Example.py"
        originalFile1 = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile2, tempFile2)        
         
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        if((os.path.exists(str(tempOutput) + "/Ref/R_to_save.csv")) & (os.path.exists(str(tempOutput) + "/R_overview/overview_output.csv"))):
            assert True
        else:
            assert False
