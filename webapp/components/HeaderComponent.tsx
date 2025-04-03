"use client";

import Link from 'next/link';
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="w-full bg-blue-600 text-white py-2 shadow-md fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex justify-between items-center">
        {/* Logo */}
        <h1 className="text-xl font-bold flex items-center space-x-2">
          <span>🚀</span>
          <span>CodeSmile</span>
        </h1>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex space-x-6">
          <Link href="/" className="hover:text-gray-300 transition-all">Home</Link>
          <Link href="/upload-python" className="hover:text-gray-300 transition-all">Upload Python</Link>
          <Link href="/upload-project" className="hover:text-gray-300 transition-all">Upload Project</Link>
          <Link href="/reports" className="hover:text-gray-300 transition-all">Reports</Link>
          <Link href="/about" className="hover:text-gray-300 transition-all">About</Link>
        </nav>

        {/* Mobile Navigation (Hamburger Menu) */}
        <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
        </button>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <motion.div
            className="md:hidden absolute top-16 right-0 w-48 bg-blue-600 p-4 rounded-lg shadow-md"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Link href="/" className="block py-2 px-4 text-white hover:bg-blue-500">Home</Link>
            <Link href="/upload-python" className="block py-2 px-4 text-white hover:bg-blue-500">Upload Python</Link>
            <Link href="/upload-project" className="block py-2 px-4 text-white hover:bg-blue-500">Upload Project</Link>
            <Link href="/reports" className="block py-2 px-4 text-white hover:bg-blue-500">Reports</Link>
            <Link href="/about" className="block py-2 px-4 text-white hover:bg-blue-500">About</Link>
          </motion.div>
        )}
      </div>
    </header>
  );
}
