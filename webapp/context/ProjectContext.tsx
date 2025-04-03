"use client";

import { ProjectType, ProjectContextType } from "@/types/types";
import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";

export const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const useProjectContext = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProjectContext must be used within a ProjectProvider");
  }
  return context;
};

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<ProjectType[]>([]);

  const addProject = () => {
    setProjects((prevProjects) => [
      ...prevProjects,
      { 
        name: "",
        files: null,
        data: { files: null, message: "", result: null, smells: null },
        isLoading: false 
      },
    ]);
  };

  const updateProject = (index: number, project: Partial<ProjectType>) => {
    setProjects((prevProjects) => {
      const updatedProjects = [...prevProjects];
      updatedProjects[index] = { ...updatedProjects[index], ...project };
      return updatedProjects;
    });
  };

  const removeProject = (index: number) => {
    setProjects((prevProjects) => prevProjects.filter((_, i) => i !== index));
  };

  // Expose the context to window for e2e testing purposes
  // Comment useEffect in production mode
  useEffect(() => {
    if (typeof window !== "undefined") {
      window.__REACT_CONTEXT__ = { projects, addProject, updateProject, removeProject };
    }
  }, [projects, addProject, updateProject, removeProject]);
  

  return (
    <ProjectContext.Provider value={{ projects, addProject, updateProject, removeProject }}>
      {children}
    </ProjectContext.Provider>
  );
};
