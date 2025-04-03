"use client";
import { useState } from "react";
import { ClipLoader } from "react-spinners";
import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import { generateReport } from "../../utils/api";
import { useProjectContext } from "../../context/ProjectContext";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import { ChartData, ContextSmell } from "@/types/types";

export default function ReportGeneratorPage() {
  const { projects } = useProjectContext();
  const [loading, setLoading] = useState<boolean>(false);
  const [chartData, setChartData] = useState<ChartData[] | null>(null);
  const [ChartSection, setChartSection] = useState<React.ComponentType<any> | null>(null);

  const handleGenerateReports = async () => {
    if (projects.length === 0) {
      toast.error("No projects available. Please add projects before generating reports.");
      return;
    }

    setLoading(true);

    try {
      // Dynamically load the ChartSection component
      const ChartSectionModule = await import("../../components/ChartSection");
      setChartSection(() => ChartSectionModule.default);

      const formattedProjects = formatProjectsData(projects);

      const areAllProjectsEmpty = formattedProjects.every(
        (project) =>
          (!project.data.smells || project.data.smells.length === 0)
      );

      if (areAllProjectsEmpty) {
        toast.info("No smell data to display.");
        setLoading(false);
        return;
      }

      const result = await generateReport(formattedProjects);

      if (result.report_data) {
        const combinedData = extractChartData(result.report_data);
        setChartData(combinedData);
       
      } else {
        throw new Error("Failed to retrieve report data.");
      }
    } catch (error) {
      console.error("Error generating reports:", error);
      toast.error("An error occurred while generating reports. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!chartData) {
      toast.error("No data available for the report.");
      return;
    }

    try {
      // Dynamically load jsPDF and autoTable
      const { jsPDF } = await import("jspdf");
      const autoTable = (await import("jspdf-autotable")).default;

      // Define jsPDFDocument type dynamically
      type jsPDFDocument = typeof jsPDF & {
        lastAutoTable: {
          finalY: number;
        };
      };

      const doc = new jsPDF();
      doc.setFontSize(18);
      doc.text("Smell Analysis Report", 14, 20);

      let currentY = 30;

      projects.forEach((project) => {
        const projectTitle = project.name || "Unnamed Project";
        doc.setFontSize(14);
        doc.text(`Project: ${projectTitle}`, 14, currentY);
        currentY += 10;

        const tableData =
          project.data.smells?.map((smell: ContextSmell) => [
            smell.smell_name,
            smell.function_name,
            smell.line,
            smell.description,
          ]) || [];

        autoTable(doc, {
          head: [["Smell Name", "Function Name", "Line", "Description"]],
          body: tableData.slice(0, 10),
          startY: currentY,
          showHead: "firstPage",
          pageBreak: "auto",
        });

        currentY = (doc as unknown as jsPDFDocument).lastAutoTable.finalY + 10;
      });

      doc.save("smell_analysis_report.pdf");
    } catch (error) {
      console.error("Error generating PDF:", error);
      toast.error("An error occurred while generating the PDF. Please try again.");
    }
  };

  const formatProjectsData = (projects: any[]) => {
    return projects.map((project) => ({
      name: project.name || "Unnamed Project",
      data: {
        files:
          project.files?.map((file: File) => ({
            name: file.name,
            size: file.size,
            type: file.type || "unknown",
            path: file.webkitRelativePath || "",
          })) || [],
        message: project.data?.message || "No message provided",
        result: project.data?.result || "No result available",
        smells: formatSmells(project.data?.smells),
      },
    }));
  };

  const formatSmells = (smells: ContextSmell[]) => {
    return (
      smells
        ?.map((smell) => {
          if (typeof smell === "string" && smell === "Static analysis returned no data") {
            return null;
          }
          if (smell && smell.smell_name) {
            return {
              smell_name: smell.smell_name,
              description: smell.description || "No description provided",
              function_name: smell.function_name || "N/A",
              line: smell.line || -1,
              additional_info: smell.additional_info || "N/A",
            };
          }
          return null;
        })
        .filter((smell) => smell !== null) || []
    );
  };

  const extractChartData = (reportData: any) => {
    const combinedData: ChartData[] = [];
    Object.keys(reportData).forEach((projectKey) => {
      const projectData = reportData[projectKey];
      projectData.forEach((item: ChartData) => combinedData.push(item));
    });
    return combinedData;
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-50 to-gray-200">
      <Header />
      <main className="flex-grow py-16 bg-gradient-to-b from-blue-50 via-blue-100 to-gray-50">
        <div className="max-w-3xl mx-auto p-8 bg-white shadow-xl rounded-2xl border border-gray-200">
          <motion.h1
            className="text-4xl font-extrabold text-blue-700 mb-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            Report Generator
          </motion.h1>

          <div className="mb-8">
            <p className="text-lg font-semibold text-gray-700">
              Total Projects Available: {projects.length}
            </p>
          </div>

          <motion.button
            onClick={handleGenerateReports}
            className="w-full bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-800 transition-all"
            disabled={loading}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {loading ? <ClipLoader size={24} color="#ffffff" data-testid="clip-loader" /> : "Generate Report"}
          </motion.button>

          {chartData && ChartSection && (
            <motion.div
              id="chart-div"
              className="mt-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <ChartSection chartData={chartData} />
              <motion.button
                onClick={handleDownloadPDF}
                className="mt-4 w-full bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Download Report as PDF
              </motion.button>
            </motion.div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
