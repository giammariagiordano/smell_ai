"use client";

import React from "react";
import { motion } from "framer-motion";
import { useProjectContext } from "../../context/ProjectContext";
import FileInput from "./FileInput";
import AnalysisResults from "./AnalysisResult";

type ProjectProps = {
  index: number;
};

const Project: React.FC<ProjectProps> = ({ index }) => {
  const { projects, updateProject, removeProject } = useProjectContext();
  const project = projects[index];

  const handleFolderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).filter(
      (file) => file.name.endsWith(".py") && file.name !== "__init__.py"
    );
    if (files.length > 0) {
      const folderName = files[0].webkitRelativePath.split("/")[0];
      updateProject(index, { files, name: folderName });
    }
  };

  return (
    <motion.div
      className="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-200 transition-transform hover:scale-105"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <h2 className="text-2xl font-semibold text-blue-700 mb-4">
        {project?.name || `Project ${index + 1}`}
      </h2>

      <FileInput onChange={handleFolderChange} />

      {project.files && (
        <motion.ul className="mt-2 text-sm text-gray-600">
          {project.files.map((file) => (
            <motion.li key={file.name} className="hover:text-blue-600">
              {file.name}
            </motion.li>
          ))}
        </motion.ul>
      )}

      <motion.button
        onClick={() => removeProject(index)}
        className="w-full bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg font-semibold hover:bg-red-700"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Remove Project
      </motion.button>

      {project.data?.result && <AnalysisResults result={project.data.result} />}
    </motion.div>
  );
};

export default Project;
