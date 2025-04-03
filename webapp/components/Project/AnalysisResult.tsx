import React from "react";

type AnalysisResultsProps = {
  result: string | null;
};

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => (
  <details className="mt-4">
    <summary className="text-blue-600 underline cursor-pointer hover:text-blue-700">
      View Analysis Results
    </summary>
    <pre className="bg-gray-100 text-sm p-4 rounded-lg mt-2 whitespace-pre-wrap overflow-x-auto">
      {result}
    </pre>
  </details>
);

export default AnalysisResults;
