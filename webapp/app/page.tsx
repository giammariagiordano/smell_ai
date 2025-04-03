"use client";

import { useRouter } from 'next/navigation';
import Header from '../components/HeaderComponent';
import Footer from '../components/FooterComponent';
import { FaArrowRight, FaUpload, FaChartBar, FaInfoCircle } from 'react-icons/fa';

export default function Home() {
  const router = useRouter();

  const navigateToUploadPython = () => {
    router.push('/upload-python');
  };

  const navigateToUploadProject = () => {
    router.push('/upload-project');
  };

  const navigateToReports = () => {
    router.push('/reports');
  };

  const navigateToAbout = () => {
    router.push('/about');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-grow pt-24 py-16 bg-gradient-to-b from-blue-50 via-blue-100 to-gray-50">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-10">
          <h1 className="text-5xl font-extrabold text-blue-600 mb-8 tracking-tight">
            Welcome to <span className="text-blue-500">CodeSmile</span> Web-App
          </h1>

          {/* Introduction section with a visual enhancement */}
          <p className="text-lg text-gray-700 mb-8">
            A modern web application to analyze Python code and projects, providing insights to improve code quality and performance.
          </p>

          {/* Button grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-8">
            {/* Upload Python Code Button */}
            <div className="flex justify-center">
              <button
                onClick={navigateToUploadPython}
                className="flex items-center justify-between w-full sm:w-80 bg-blue-500 text-white px-6 py-4 rounded-xl shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300 transition-all transform hover:scale-105"
              >
                <span className="text-xl">Analyze Python Code</span>
                <FaUpload className="text-white text-2xl" />
              </button>
            </div>

            {/* Upload Project Folder Button */}
            <div className="flex justify-center">
              <button
                onClick={navigateToUploadProject}
                className="flex items-center justify-between w-full sm:w-80 bg-green-500 text-white px-6 py-4 rounded-xl shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300 transition-all transform hover:scale-105"
              >
                <span className="text-xl">Analyze Project</span>
                <FaArrowRight className="text-white text-2xl" />
              </button>
            </div>

            {/* Generate Reports Button */}
            <div className="flex justify-center">
              <button
                onClick={navigateToReports}
                className="flex items-center justify-between w-full sm:w-80 bg-yellow-500 text-white px-6 py-4 rounded-xl shadow-md hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-300 transition-all transform hover:scale-105"
              >
                <span className="text-xl">Generate Reports</span>
                <FaChartBar className="text-white text-2xl" />
              </button>
            </div>

            {/* About Button */}
            <div className="flex justify-center">
              <button
                onClick={navigateToAbout}
                className="flex items-center justify-between w-full sm:w-80 bg-gray-600 text-white px-6 py-4 rounded-xl shadow-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-all transform hover:scale-105"
              >
                <span className="text-xl">About CodeSmile</span>
                <FaInfoCircle className="text-white text-2xl" />
              </button>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
