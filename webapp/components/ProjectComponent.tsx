"use client";

import React, { useRef, useEffect } from "react";
import { useProjectContext } from "../context/ProjectContext";
import { motion } from "framer-motion";

type ProjectProps = {
  index: number;
};

const Project: React.FC<ProjectProps> = ({ index }) => {
  const { projects, updateProject, removeProject } = useProjectContext();
  const project = projects[index];
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (fileInputRef.current) {
      (fileInputRef.current as HTMLInputElement).webkitdirectory = true;
    }
  }, []);

  const handleFolderChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    const files = fileList ? Array.from(fileList) : [];
    const filteredFiles = files.filter((file) => file.name.endsWith(".py") && file.name !== "__init__.py");

    if (filteredFiles.length > 0) {
      // Extract the folder name from the file path
      const folderName = filteredFiles[0].webkitRelativePath.split("/")[0];
      updateProject(index, {
        files: filteredFiles,
        name: folderName,
      });
    }
  };

  return (
    <motion.div
      className="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-200 transition-transform hover:scale-105"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <h2 className="text-2xl font-semibold text-blue-700 mb-4">{project?.name || `Project ${index + 1}`}</h2>

      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFolderChange}
        className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg mb-4 cursor-pointer hover:bg-gray-100 transition-all duration-300"
        multiple
        data-testid="file-input" 
      />

      {/* Display Files */}
      {project.files && project.files.length > 0 && (
        <motion.ul
          className="mt-2 text-sm text-gray-600"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {Array.from(project.files).map((file) => (
            <motion.li key={file.name} className="hover:text-blue-600" whileHover={{ scale: 1.05 }}>
              {file.name}
            </motion.li>
          ))}
        </motion.ul>
      )}

      {/* Remove Project Button */}
      <motion.button id="removeButton"
        onClick={() => removeProject(index)}
        className="w-full bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg font-semibold hover:bg-red-700 transition-all mt-4"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Remove Project
      </motion.button>

      {/* Display Message */}
      {project.data?.message && (
        <p id="message"
          className={`mt-4 text-center font-medium text-lg ${project.data.message.includes("Error") ? "text-red-500" : "text-green-600"}`}
        >
          {project.data.message}
        </p>
      )}

      {/* View Analysis Results */}
      {project.data?.result && (
        <motion.details className="mt-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
          <summary className="text-blue-600 underline cursor-pointer hover:text-blue-700">
            View Analysis Results
          </summary>
          <pre className="bg-gray-100 text-sm p-4 rounded-lg mt-2 whitespace-pre-wrap overflow-x-auto">
            {project.data.result}
          </pre>
        </motion.details>
      )}
    </motion.div>
  );
};

export default Project;
