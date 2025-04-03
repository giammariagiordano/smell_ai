"use client";

import Header from "../../components/HeaderComponent";
import Footer from "../../components/FooterComponent";
import { FaRocket, FaCode, FaClipboardList } from "react-icons/fa";

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-grow py-16 bg-gradient-to-b from-blue-50 via-blue-100 to-gray-50">
        <div className="max-w-5xl mx-auto px-6 py-10 bg-white shadow-xl rounded-xl space-y-10">
          <h1 className="text-5xl font-extrabold text-blue-700 mb-6 tracking-tight text-center">
            About <span className="text-blue-500">CodeSmile</span>
          </h1>

          <section className="space-y-8 text-lg text-gray-800">
            <p className="leading-relaxed text-xl">
              <strong className="font-semibold text-blue-700">CodeSmile</strong> is an innovative web application designed to analyze and identify code smells within Python codebases. It helps developers maintain cleaner and more efficient code by providing detailed insights and actionable recommendations based on static code analysis.
            </p>

            <p className="leading-relaxed text-xl">
              Whether you&apos;re a novice or an experienced developer, CodeSmile assists you in improving code quality, ensuring best practices, and optimizing the performance of your Python projects.
            </p>

            <h2 className="text-3xl font-semibold text-blue-700 mt-12 mb-6 text-center">Our Mission</h2>
            <p className="leading-relaxed text-xl">
              Our mission is to make coding a more efficient and enjoyable experience for developers. By offering fast and accurate analysis of code smells, we help developers identify issues early in the development process, ensuring the production of high-quality software.
            </p>

            <h2 className="text-3xl font-semibold text-blue-700 mt-12 mb-6 text-center">Key Features</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="bg-gray-100 p-6 rounded-lg shadow-md hover:shadow-xl transition-all">
                <FaRocket className="text-blue-500 text-4xl mb-4" />
                <h3 className="text-2xl font-semibold text-gray-800 mb-4">Easy File Upload</h3>
                <p className="text-lg text-gray-600">
                  Upload Python files or entire project folders for analysis with a simple drag-and-drop interface.
                </p>
              </div>
              <div className="bg-gray-100 p-6 rounded-lg shadow-md hover:shadow-xl transition-all">
                <FaCode className="text-blue-500 text-4xl mb-4" />
                <h3 className="text-2xl font-semibold text-gray-800 mb-4">Instant Feedback</h3>
                <p className="text-lg text-gray-600">
                  Get instant feedback on code smells and actionable recommendations to improve your code quality.
                </p>
              </div>
              <div className="bg-gray-100 p-6 rounded-lg shadow-md hover:shadow-xl transition-all">
                <FaClipboardList className="text-blue-500 text-4xl mb-4" />
                <h3 className="text-2xl font-semibold text-gray-800 mb-4">Track Progress</h3>
                <p className="text-lg text-gray-600">
                  Generate detailed reports to track improvements and identify areas for optimization over time.
                </p>
              </div>
            </div>
          </section>

          <div className="mt-10 text-lg text-gray-600 text-center space-y-4">
            <p>Want to learn more or get in touch with us?</p>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-all">
              Contact Us
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
