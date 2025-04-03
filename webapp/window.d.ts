import { ProjectType } from './types/types'

// window.d.ts, support for e2e cypress testing
export {}; 

declare global {
  interface Window {
    __REACT_CONTEXT__?: {
      projects: ProjectType[];
      addProject: () => void;
      updateProject: (index: number, project: Partial<ProjectType>) => void;
      removeProject: (index: number) => void;
    };
  }
}
