export type ContextSmell = {
  function_name: string;
  line: number;
  smell_name: string;
  description: string;
  additional_info: string;
};

export type DetectResponse = {
    success: boolean;
    smells: ContextSmell[];
}

export type GenerateReportResponse = {
    report_data: Record<string, any>;
}

export type ChartData = { 
  smell_name: string;
  filename: string 
};

export type ProjectType = {
  name: string;
  files: File[] | null;
  data: {
    files: string[] | null;
    message: string;
    result: string | null;
    smells: ContextSmell[] | null;
  };
  isLoading: boolean;
};

export type ProjectContextType = {
  projects: ProjectType[];
  addProject: () => void;
  updateProject: (index: number, project: Partial<ProjectType>) => void;
  removeProject: (index: number) => void;
};
