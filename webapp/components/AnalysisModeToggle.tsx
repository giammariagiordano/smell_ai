// components/AnalysisModeToggle.tsx
import React from "react";
import { motion } from "framer-motion";

type AnalysisModeToggleProps = {
  analysisMode: "AI" | "Static";
  setAnalysisMode: React.Dispatch<React.SetStateAction<"AI" | "Static">>;
};

const AnalysisModeToggle: React.FC<AnalysisModeToggleProps> = ({
  analysisMode,
  setAnalysisMode,
}) => {
  return (
    <motion.div
      className="mb-8 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <label className="block mb-4 font-semibold text-xl text-gray-700">
        Select Analysis Mode:
      </label>
      <div className="flex justify-center space-x-6">
        <motion.button
          onClick={() => setAnalysisMode("AI")}
          className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
            analysisMode === "AI"
              ? "bg-red-600 text-white shadow-xl"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          } hover:scale-105`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          AI-Based
        </motion.button>
        <motion.button
          onClick={() => setAnalysisMode("Static")}
          className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
            analysisMode === "Static"
              ? "bg-blue-600 text-white shadow-xl"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          } hover:scale-105`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Static Tool
        </motion.button>
      </div>
    </motion.div>
  );
};

export default AnalysisModeToggle;
