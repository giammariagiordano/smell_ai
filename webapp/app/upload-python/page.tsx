"use client";
import { toast } from "react-toastify";
import { useState } from "react";
import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import { detectAi, detectStatic } from "../../utils/api";
import { motion } from "framer-motion";
import { ContextSmell, DetectResponse } from "@/types/types";

function ProgressBar({ progress }: { progress: number }) {
  return (
    <motion.div
      
      className="mt-6 w-full bg-gray-200 rounded-full"
      initial={{ width: 0 }}
      animate={{ width: `${progress}%` }}
      transition={{ duration: 3, ease: "easeInOut" }}
    >
      <div className="h-2 bg-blue-500 rounded-full" data-testid="progress" id="progress-bar"></div>
    </motion.div>
  );
}

function AnalysisModeToggle({
  analysisMode,
  setAnalysisMode,
}: {
  analysisMode: "AI" | "Static";
  setAnalysisMode: React.Dispatch<React.SetStateAction<"AI" | "Static">>;
}) {
  return (
    <div className="mb-10 text-center">
      <label className="block text-xl font-semibold text-gray-700 mb-4">
        Select Analysis Mode:
      </label>
      <div className="flex justify-center space-x-6">
        <motion.button
          onClick={() => setAnalysisMode("AI")}
          className={`px-8 py-4 rounded-lg font-medium transition-all ${
            analysisMode === "AI"
              ? "bg-red-500 text-white shadow-md"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          AI-Based
        </motion.button>
        <motion.button
          onClick={() => setAnalysisMode("Static")}
          className={`px-8 py-4 rounded-lg font-medium transition-all ${
            analysisMode === "Static"
              ? "bg-blue-500 text-white shadow-md"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Static Tool
        </motion.button>
      </div>
    </div>
  );
}

function FileUploadSection({
  fileName,
  handleFileChange,
}: {
  fileName: string;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div className="mb-10 text-center">
      <label
        htmlFor="file-upload"
        className="block text-xl font-semibold text-gray-700 mb-4"
      >
        Select a Python File:
      </label>
      <input
        id="file-upload"
        role="file-uploader"
        type="file"
        accept=".py"
        onChange={handleFileChange}
        className="w-full p-6 bg-gray-100 border border-gray-300 rounded-md cursor-pointer hover:bg-gray-200 transition-all"
      />
      {fileName && (
        <p className="mt-2 text-lg text-gray-700" data-testid="filename" id="file-name">
          <strong>Selected File:</strong> {fileName}
        </p>
      )}
    </div>
  );
}

function Results({ result, fileName }: { result: ContextSmell[] | null; fileName: string }) {
  if (!result) return null;

  if (result.length === 0) {
    return (
      <motion.p
        className="mt-8 text-xl text-center text-green-600"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        No code smells detected! Your code is clean!
      </motion.p>
    );
  }

  return (
    <motion.div
      className="mt-8 space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {result.map((smell, index) => (
        <div
          key={index}
          className="bg-gray-100 p-6 rounded-lg shadow-lg border border-gray-300"
        >
          <h3 className="font-semibold text-2xl text-blue-600 mb-2">
            Smell #{index + 1}
          </h3>
          {smell.description && (
            <p className="text-lg font-medium text-gray-800">
              <strong>Description:</strong> {smell.description}
            </p>
          )}
          {fileName && (
            <p className="text-lg text-gray-700">
              <strong>File Name:</strong> {fileName}
            </p>
          )}
          {smell.smell_name && (
            <p className="text-lg text-gray-700">
              <strong>Smell:</strong> {smell.smell_name}
            </p>
          )}
          {smell.function_name && (
            <p className="text-lg text-gray-700">
              <strong>Function Name:</strong> {smell.function_name}
            </p>
          )}
          {smell.line && (
            <p className="text-lg text-gray-700">
              <strong>Line:</strong> {smell.line}
            </p>
          )}
          {smell.additional_info && (
            <p className="text-lg text-gray-700">
              <strong>Additional Info:</strong> {smell.additional_info}
            </p>
          )}
        </div>
      ))}
    </motion.div>
  );
}

export default function UploadPythonPage() {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ContextSmell[] | null>(null);
  const [analysisMode, setAnalysisMode] = useState<"AI" | "Static">("AI");
  const [progress, setProgress] = useState<number>(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files ? e.target.files[0] : null;
    setFile(uploadedFile);
    setFileName(uploadedFile ? uploadedFile.name : "");
  };

  const handleSubmit = async () => {
    if (!file) {
      setIsLoading(false);
      setProgress(100)
      toast.error("No file available. Please add a file before submitting.")
      return;
    }

    const fileContent = await file.text();

    if(!fileContent) {
      setIsLoading(false);
      setProgress(100)
      toast.error("Code Snippet cannot be empty.");
      return
    }

    setIsLoading(true);
    toast.info("Uploading and analyzing code...");
    setProgress(30);

    const data: DetectResponse =
      analysisMode === "AI"
        ? await detectAi(fileContent)
        : await detectStatic(fileContent);

    setProgress(70);

    if(!data.success) {
      toast.error(`Error: Failed to analyze code.`);
      setIsLoading(false);
      setProgress(100);
      return;
    }

    if (data.smells) {
      setResult(data.smells);
      toast.success("Code uploaded and analyzed successfully!");
      setIsLoading(false);
      setProgress(100);    
      
    } else {
      toast.error("Unexpected API response format");
      setIsLoading(false);
      setProgress(100);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-grow py-16 bg-gradient-to-b from-blue-50 via-blue-100 to-gray-50">
        <div className="max-w-3xl mx-auto p-8 bg-white shadow-xl rounded-lg">
          {/* Page Title */}
          <motion.h1
            className="text-4xl font-extrabold text-center text-blue-600 mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            Upload and Analyze Python Code
          </motion.h1>

          {/* Analysis Mode Toggle */}
          <AnalysisModeToggle analysisMode={analysisMode} setAnalysisMode={setAnalysisMode} />

          {/* File Upload Section */}
          <FileUploadSection
            fileName={fileName}
            handleFileChange={handleFileChange}
          />

          {/* Submit Button */}
          <motion.button
            onClick={handleSubmit}
            className={`w-full px-8 py-4 rounded-lg shadow-md transition-all font-medium ${
              isLoading ? "bg-red-500 text-white" : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
            disabled={isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin border-t-2 border-b-2 border-white rounded-full w-6 h-6 mr-2"></div>
                Uploading and Analyzing...
              </div>
            ) : (
              `Upload Code (${analysisMode} Mode)`
            )}
          </motion.button>

          {/* Progress Bar */}
          {isLoading && <ProgressBar progress={progress} />}

          {/* Results */}
          <Results result={result} fileName={fileName} />
        </div>
      </main>

      <Footer />
    </div>
  );
}
