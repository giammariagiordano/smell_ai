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
        
    def test_RA_1(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        assert args.refactor is True
        
    def test_RM_1_1(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2
                
    def test_RM_1_2(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 3
        
    def test_RM_1_3(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2   
        
    def test_RM_1_4(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)  
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        assert not (os.path.exists(str(fullpath) + "/1/to_save.csv")) #In tal caso, è avvenuto return per assenza di file.
        
    def test_RM_1_5(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Non_Refactor_Smell_Examples.py"
        originalFile = '../input/projects/example/Non_Refactor_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)       
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        assert ((os.path.exists(str(fullpath) + "/1/Ref/R_to_save.csv")) and not (os.path.exists(tempOutput / "R_overview"/ "overview_output.csv")))


        
    def test_RM_1_6(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempDir2 = tmp_path / "project/project2"
        tempDir2.mkdir()
        tempFile1 = tempDir / "Non_Refactor_Smell_Examples.py"
        tempFile2 = tempDir2 / "Single_Smell_Non_Refactor_Example.py"
        originalFile1 = '../input/projects/example/Non_Refactor_Smell_Examples.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Single_Smell_Non_Refactor_Example.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tmp_path), "--output", str(tempOutput), "--refactor", "--multiple", "True"])
        analyzer.main(args)
        
        if(os.path.exists(tempOutput / "project1" / "to_save.csv") & os.path.exists(tempOutput / "project2" / "to_save.csv")):
            if(not os.path.exists(tempOutput / "R_overview")):
                assert True    
            else:
                assert False
    
    def test_RM_1_7(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Single_Smell_Example.py"
        originalFile = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile, tempFile)       
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        with open(str(tempFile), "r", encoding="utf-8") as file:
            source = file.readlines()
            if "net" in source[7]:
                assert ((os.path.exists(str(fullpath) + "/1/Ref/R_to_save.csv")) and (os.path.exists(tempOutput / "R_overview"/ "overview_output.csv")))
            else:
                assert False
    
    def test_RM_1_8(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempDir2 = tmp_path / "project/project2"
        tempDir2.mkdir()
        tempFile1 = tempDir / "Non_Refactor_Smell_Examples.py"
        tempFile2 = tempDir2 / "Single_Smell_Example.py"
        originalFile1 = '../input/projects/example/Non_Refactor_Smell_Examples.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tmp_path), "--output", str(tempOutput), "--refactor", "--multiple", "True"])
        analyzer.main(args)
        
        if(os.path.exists(tempOutput / "project1" / "Ref/R_to_save.csv") & os.path.exists(tempOutput / "project2" / "Ref/R_to_save.csv")):
            if(os.path.exists(tempOutput / "R_overview/overview_output.csv")):
                with open(str(tempFile2), "r", encoding="utf-8") as file:
                    source = file.readlines()
                    assert "net" in source[7]
            else:
                assert False
                
    def test_RM_1_9(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Code_Smell_Examples.py"
        originalFile = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)       
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        
        if(os.path.exists(tempOutput / "project1" / "Ref/R_to_save.csv")):
            if(os.path.exists(tempOutput / "R_overview/overview_output.csv")):
                with open(str(tempFile), "r", encoding="utf-8") as file:
                    source = file.readlines()
                    assert("to_numpy" in source[196] and "np.nan" in source[129] and "np.nan" in source[130] and "zero_grad" in source[146] and "np.matmul" in source[186] and "np.isnan" in source[124] and "net" in source[166] and "tf.TensorArray" in source[174])
            else:
                assert False
    
    def test_RM_1_10(self, parse, tmp_path):    
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempDir2 = tmp_path / "project/project2"
        tempDir2.mkdir()
        tempFile1 = tempDir / "Code_Smell_Examples.py"
        tempFile2 = tempDir2 / "Single_Smell_Example.py"
        originalFile1 = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tmp_path), "--output", str(tempOutput), "--refactor", "--multiple", "True"])
        analyzer.main(args)
        
        if(os.path.exists(tempOutput / "project1" / "Ref/R_to_save.csv") & os.path.exists(tempOutput / "project2" / "Ref/R_to_save.csv")):
            if(os.path.exists(tempOutput / "R_overview/overview_output.csv")):
                with open(str(tempFile), "r", encoding="utf-8") as file:
                    source1 = file.readlines()
                    with open(str(tempFile2), "r", encoding="utf-8") as file2:
                        source2 = file2.readlines()
                        assert("to_numpy" in source1[196] and "np.nan" in source1[129] and "np.nan" in source1[130] and "zero_grad" in source1[146] and "np.matmul" in source1[186] and "np.isnan" in source1[124] and "net" in source1[166] and "tf.TensorArray" in source1[174] and "net" in source2[7])
            else:
                assert False
    
    def test_RC_1_1(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2
                
    def test_RC_1_2(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 3
        
    def test_RC_1_3(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2   
        
    def test_RC_1_4(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)  
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        assert not (os.path.exists(str(fullpath) + "/1/to_save.csv")) #In tal caso, è avvenuto return per assenza di file.
    
    def test_RC_1_5(self, parse, tmp_path):
        
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Non_Refactor_Smell_Examples.py"
        originalFile = '../input/projects/example/Non_Refactor_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        with open(str(originalFile), "r", encoding="utf-8") as file1:
            source1 = file1.readlines()
            with open(str(tempFile), "r", encoding="utf-8") as file2:
                source2 = file2.readlines()
                assert set(source1) == set(source2)
                
    def test_RC_1_6(self, parse, tmp_path):
        
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Single_Smell_Example.py"
        originalFile = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        with open(str(tempFile), "r", encoding="utf-8") as file:
            source = file.readlines()
            assert "net" in source[7]
    
    def test_RC_1_7(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile1 = tempDir / "Single_Smell_Example.py"
        tempFile2 = tempDir / "Code_Smell_Examples.py"
        originalFile1 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        with open(str(tempFile1), "r", encoding="utf-8") as file:
            source1 = file.readlines()
            with open(str(tempFile2), "r", encoding="utf-8") as file2:
                source2 = file2.readlines()
                assert("to_numpy" in source2[196] and "np.nan" in source2[129] and "np.nan" in source2[130] and "zero_grad" in source2[146] and "np.matmul" in source2[186] and "np.isnan" in source2[124] and "net" in source2[166] and "tf.TensorArray" in source2[174] and "net" in source1[7])
    
    def test_RS_1_1(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2
                
    def test_RS_1_2(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 3
        
    def test_RS_1_3(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        with pytest.raises(SystemExit) as error:
            analyzer.main(args)
        assert error.value.code == 2   
        
    def test_RS_1_4(self, parse, tmp_path):
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project"
        tempDir.mkdir()
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)  
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        assert not (os.path.exists(str(fullpath) + "/1/to_save.csv")) #In tal caso, è avvenuto return per assenza di file.
    
    
    def test_RS_1_5(self, parse, tmp_path):  
           
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Non_Refactor_Smell_Examples.py"
        originalFile = '../input/projects/example/Non_Refactor_Smell_Examples.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        if((os.path.exists(str(fullpath) + "/1/Ref/R_to_save.csv")) and not (os.path.exists(str(tempOutput) + "/R_overview"))):
            df = pandas.read_csv(str(fullpath) + "/1/Ref/R_to_save.csv")
            oracle = {'filename': {}, 'function_name': {}, 'smell_name': {}, 'line': {}
            }
            assert df.to_dict() == oracle
        else:
            assert False
            
    def test_RS_1_6(self, parse, tmp_path):  
           
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile = tempDir / "Single_Smell_Example.py"
        originalFile = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile, tempFile)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        if((os.path.exists(str(fullpath) + "/1/Ref/R_to_save.csv")) and (os.path.exists(str(tempOutput) + "/R_overview"))):
            df = pandas.read_csv(str(fullpath) + "/1/Ref/R_to_save.csv")
            oracle = {'filename': {0: str(tempFile), 1: str(tempFile)}, 'function_name': {0: "newFunction", 1: "newFunction"}, 'smell_name': {0: "pytorch_call_method_misused", 1: "pytorch_call_method_misused"}, 'line': {0: 8, 1: 8}
            }
            
            df2 = pandas.read_csv(str(tempOutput) + "/R_overview/overview_output.csv")
            oracle2 = {'index': {0: 0, 1: 1}, 'filename': {0: str(tempFile), 1: str(tempFile)}, 'function_name': {0: "newFunction", 1: "newFunction"}, 'smell_name': {0: "pytorch_call_method_misused", 1: "pytorch_call_method_misused"}, 'line': {0: 8, 1: 8}
            }
            assert df.to_dict() == oracle and df2.to_dict() == oracle2
        else:
            assert False
            
    def test_RS_1_7(self, parse, tmp_path):  
           
        tempOutput = tmp_path / "output"
        tempOutput.mkdir()
        tempDir = tmp_path / "project/project1"
        tempDir.parent.mkdir()
        tempDir.mkdir()
        tempFile1 = tempDir / "Single_Smell_Example.py"
        tempFile2 = tempDir / "Code_Smell_Examples.py"
        originalFile1 = '../input/projects/example/Single_Smell_Example.py'
        shutil.copyfile(originalFile1, tempFile1)
        originalFile2 = '../input/projects/example/Code_Smell_Examples.py'
        shutil.copyfile(originalFile2, tempFile2)        
        args = parse.parse_args(["--input", str(tempDir), "--output", str(tempOutput), "--refactor"])
        analyzer.main(args)
        fullpath = os.path.join(str(tempOutput), os.path.basename(os.path.normpath(args.input)))
        if((os.path.exists(str(fullpath) + "/1/Ref/R_to_save.csv")) and (os.path.exists(str(tempOutput) + "/R_overview"))):
            df = pandas.read_csv(str(fullpath) + "/1/Ref/R_to_save.csv")
            oracle = {'filename': {0: str(tempFile2), 1: str(tempFile2), 2: str(tempFile2), 3: str(tempFile2), 4: str(tempFile2), 5: str(tempFile2), 6: str(tempFile2), 7: str(tempFile2), 8: str(tempFile1), 9: str(tempFile1), 10: str(tempFile2)}, 
            'function_name': {0: "dataframe_conversion_api_misused_example", 1: "empty_example", 2: "empty_example", 3: "gradient_not_cleared_before_backward_propagation" , 4: "matrix_mul_example", 5: "nan_equivalence_example2" , 6: "pytorch_call_method_misused_example2", 7: "pytorch_call_method_misused_example2", 8: "newFunction", 9: "newFunction", 10: "tensor_example"},
            'smell_name': {0: "dataframe_conversion_api_misused", 1: "empty_column_misinitialization", 2: "empty_column_misinitialization", 3: "gradients_not_cleared_before_backward_propagation" , 4: "matrix_multiplication_api_misused", 5: "nan_equivalence_comparison_misused" , 6: "pytorch_call_method_misused", 7: "pytorch_call_method_misused", 8: "pytorch_call_method_misused", 9: "pytorch_call_method_misused", 10: "tensor_array_not_used"},
            'line': {0: 197, 1: 130, 2: 131, 3: 147 , 4: 187, 5: 125 , 6: 167, 7: 167, 8: 8, 9: 8, 10: 174}
            }
            
            df2 = pandas.read_csv(str(tempOutput) + "/R_overview/overview_output.csv")
            oracle2 = {'index': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}, 'filename': {0: str(tempFile2), 1: str(tempFile2), 2: str(tempFile2), 3: str(tempFile2), 4: str(tempFile2), 5: str(tempFile2), 6: str(tempFile2), 7: str(tempFile2), 8: str(tempFile1), 9: str(tempFile1), 10: str(tempFile2)}, 
            'function_name': {0: "dataframe_conversion_api_misused_example", 1: "empty_example", 2: "empty_example", 3: "gradient_not_cleared_before_backward_propagation" , 4: "matrix_mul_example", 5: "nan_equivalence_example2" , 6: "pytorch_call_method_misused_example2", 7: "pytorch_call_method_misused_example2", 8: "newFunction", 9: "newFunction", 10: "tensor_example"},
            'smell_name': {0: "dataframe_conversion_api_misused", 1: "empty_column_misinitialization", 2: "empty_column_misinitialization", 3: "gradients_not_cleared_before_backward_propagation" , 4: "matrix_multiplication_api_misused", 5: "nan_equivalence_comparison_misused" , 6: "pytorch_call_method_misused", 7: "pytorch_call_method_misused", 8: "pytorch_call_method_misused", 9: "pytorch_call_method_misused", 10: "tensor_array_not_used"},
            'line': {0: 197, 1: 130, 2: 131, 3: 147 , 4: 187, 5: 125 , 6: 167, 7: 167, 8: 8, 9: 8, 10: 174}
            }
            assert df.to_dict() == oracle and df2.to_dict() == oracle2
        else:
            assert False
