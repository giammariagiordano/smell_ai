"use client";

import { FaLinkedin, FaGithub } from 'react-icons/fa';

export default function Footer() {
  return (
    <footer className="w-full bg-gray-800 text-white py-4 mt-8">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-xs">&copy; 2025 CodeSmile. All rights reserved.</p>
        
        <div className="mt-2 space-x-6">
          <a href="#" className="hover:text-gray-400">
            <FaLinkedin size={20} />
          </a>
          <a href="#" className="hover:text-gray-400">
            <FaGithub size={20} />
          </a>
        </div>

        <div className="mt-2 space-x-4">
          <a href="#" className="hover:text-gray-400">Privacy Policy</a>
          <a href="#" className="hover:text-gray-400">Terms of Service</a>
        </div>
      </div>
    </footer>
  );
}
