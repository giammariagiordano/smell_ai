"use client";
import { useState } from "react";
import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import Project from "../../components/ProjectComponent";
import { useProjectContext } from "../../context/ProjectContext";
import { detectAi, detectStatic } from "../../utils/api";
import { motion } from "framer-motion";
import AnalysisModeToggle from "../../components/AnalysisModeToggle";
import Button from "../../components/Button"; 
import { toast } from "react-toastify";

const UploadProjectPage = () => {
  const { projects, addProject, updateProject } = useProjectContext();
  const [analysisMode, setAnalysisMode] = useState<"AI" | "Static">("AI");

  // Handle the submission of all projects for analysis
  const handleSubmitAll = async () => {
    setProjectsLoadingState(true);

    try {
      const resolvedSnippets = await prepareCodeSnippets();
      const results = await analyzeCodeSnippets(resolvedSnippets);

      updateProjectsWithAnalysisResults(results);
    } catch (error) {
      toast.error("Error during project analysis");
      resetProjectsOnError();
    }
  };

  const setProjectsLoadingState = (isLoading: boolean) => {
    projects.forEach((_, index) => {
      updateProject(index, {
        files: null,
        isLoading,
        data: { files: null,
          message: isLoading ? "Uploading and analyzing the project..." : "Error analyzing project.",
          result: null,
          smells: null },
      });
    });
  };

  const prepareCodeSnippets = async () => {
    return await Promise.all(
      projects.flatMap((project) =>
        project.files ? project.files.map(async (file) => {
          const content = await file.text();
          return { file, content };
        }) : []
      )
    );
  };

 const analyzeCodeSnippets = async (resolvedSnippets: any[]) => {
    return await Promise.all(
      resolvedSnippets.map(async (snippet) => {
        try {
          const result =
            analysisMode === "AI"
              ? await detectAi(snippet.content)
              : await detectStatic(snippet.content);

          if (result?.success === false) {
            toast.error(
              `Analysis failed for snippet: ${snippet.file.name}`
            );
          }
          return result;
        } catch (error: any) {
          if (error?.data?.success === false) {
            toast.error(
              `Error analyzing snippet: ${snippet.file.name} - ${error.data.message || "Unknown error"}`
            );
          } else {
            // Generic error fallback
            toast.error(`Unexpected error analyzing snippet: ${snippet.file.name}`);
          }

          return {
            smells: [],
          };
        }
      })
    );
  };

  const updateProjectsWithAnalysisResults = (results: any[]) => {
    let resultIndex = 0;

    projects.forEach((project, index) => {
      if (project.files) {
        const projectFiles = Array.from(project.files).filter((file) => file.name.endsWith(".py"));
        const projectResults = results.slice(resultIndex, resultIndex + projectFiles.length);
        resultIndex += projectFiles.length;

        const resultString = generateResultString(projectResults, projectFiles);

        updateProject(index, {
          files: projectFiles.map((file) => file),
          data: {
            files: projectFiles.map((file) => file.name),
            message: "Projects successfully analyzed!",
            result: resultString,
            smells: projectResults.flatMap((result) => result.smells) || [],
          },
          isLoading: false,
        });
      } else {
        updateProject(index, {
          files: null,
          data: {
            files: null,
            message: "Error, no valid files to analyze.",
            result: null,
            smells: [],
          },
          isLoading: false,
        });
      }
    });
  };

  const generateResultString = (projectResults: any[], projectFiles: any[]) => {
    return projectResults
      .map((res, fileIndex) => {
        const fileName = projectFiles[fileIndex].name;
        const smells = Array.isArray(res.smells) ? res.smells : [];
        return `File: ${fileName}\n` + smells
          .map((smell: { function_name: any; line: any; smell_name: any; description: any; additional_info: any; }) => {
            let result = "";
            if (smell.function_name) result += `Function: ${smell.function_name}\n`;
            if (smell.line) result += `Line: ${smell.line}\n`;
            if (smell.smell_name) result += `Smell: ${smell.smell_name}\n`;
            if (smell.description) result += `Description: ${smell.description}\n`;
            if (smell.additional_info) result += `Additional Info: ${smell.additional_info}\n`;
            return result.trim();
          })
          .join("\n\n");
      })
      .join("\n\n");
  };

  const resetProjectsOnError = () => {
    projects.forEach((_, index) => {
      updateProject(index, {
        files: null,
        data: {
          files: null,
          message: "Error analyzing project.",
          result: null,
          smells: [],
        },
        isLoading: false,
      });
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-blue-100 to-gray-200">
      <Header />

      <main className="flex-grow py-16 bg-gradient-to-b from-purple-50 via-indigo-100 to-gray-50">
        <div className="max-w-4xl mx-auto p-8 bg-white shadow-2xl rounded-3xl border border-gray-200">
          <motion.h1
            className="text-5xl font-extrabold text-blue-700 mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            Upload and Analyze Projects
          </motion.h1>

          {/* Analysis Mode Toggle */}
          <AnalysisModeToggle analysisMode={analysisMode} setAnalysisMode={setAnalysisMode} />

          {/* Add Project Button */}
          <Button
            onClick={addProject}
            className="w-full bg-green-600 text-white px-6 py-3 rounded-xl shadow-xl font-semibold hover:bg-green-700 transition-all duration-300 mb-6"
            disabled={false}
          >
            Add Project
          </Button>

          {/* Project List */}
          <div className="space-y-6">
            {projects.map((_, index) => (
              <Project key={index} index={index} />
            ))}
          </div>

          {/* Submit All Projects Button */}
          <Button
            onClick={handleSubmitAll}
            className="w-full px-6 py-3 rounded-xl shadow-lg bg-blue-600 text-white hover:bg-blue-700 transition-all duration-300 mb-6"
            disabled={projects.some((project) => project.isLoading) || projects.length === 0}
            
          >
          {projects.some((project) => project.isLoading)
            ? "Analyzing Projects..."
            : "Upload and Analyze All Projects"}
        </Button>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default UploadProjectPage;
