/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface AUTWindow {
      __REACT_CONTEXT__?: {
        projects: ProjectType[];
        addProject: () => void;
        updateProject: (index: number, project: Partial<ProjectType>) => void;
        removeProject: (index: number) => void;
      };
    }
  }
}
