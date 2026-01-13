// FILE: src/components/layout/Footer.jsx
// ============================================================================

import { Link } from 'react-router-dom';
import { 
  BookOpen, 
  Brain, 
  UploadCloud, 
  Mail, 
  Code,
  FileText,
  Scale,
  Shield
} from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <BookOpen className="w-8 h-8 text-primary-400" />
              <span className="text-xl font-bold">SK-LearnTrack</span>
            </div>
            <p className="text-gray-400 mb-4">
              Your all-in-one platform for mastering any skill with AI-powered tools.
            </p>

          </div>
          
          {/* Modules Column */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Modules</h4>
            <ul className="space-y-2 text-gray-400">
              <li>
                <Link to="/courses" className="hover:text-primary-400 transition-colors flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Courses
                </Link>
              </li>
              <li>
                <Link to="/notes" className="hover:text-primary-400 transition-colors flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Study Notes
                </Link>
              </li>
              <li>
                <Link to="/roadmap" className="hover:text-primary-400 transition-colors flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Roadmapper
                </Link>
              </li>
              <li>
                <Link to="/analytics" className="hover:text-primary-400 transition-colors flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  Analytics
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Features Column */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Features</h4>
            <ul className="space-y-2 text-gray-400">
              <li className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                <span>AI Tools</span>
              </li>
              <li className="flex items-center gap-2">
                <UploadCloud className="w-4 h-4" />
                <span>Cloud Export</span>
              </li>
              <li className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <span>Daily Reports</span>
              </li>
              <li className="flex items-center gap-2">
                <Code className="w-4 h-4" />
                <span>Code Execution</span>
              </li>
            </ul>
          </div>
          
          {/* Contact Column */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Contact</h4>
            <ul className="space-y-2 text-gray-400">
              <li>
                <a 
                  href="mailto:shahriyarkhanpk1@gmail.com" 
                  className="hover:text-primary-400 transition-colors"
                >
                  shahriyarkhanpk1@gmail.com
                </a>
              </li>
              <li>Support: support@sklearntrack.com</li>
              <li>Islamabad, Pakistan</li>
            </ul>
          </div>
        </div>
        
        {/* Footer Bottom */}
        <div className="pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-center md:text-left">
              &copy; {currentYear} SK-LearnTrack. All rights reserved.
            </p>
            
            <div className="flex items-center gap-6">
              <Link 
                to="/privacy-policy" 
                className="text-gray-400 hover:text-primary-400 transition-colors text-sm"
              >
                Privacy Policy
              </Link>
              <Link 
                to="/terms-of-service"
                className="text-gray-400 hover:text-primary-400 transition-colors text-sm"
              >
                Terms of Service
              </Link>
            </div>
          </div>
          
          {/* Google OAuth Compliance Note */}
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-xs">
              Google OAuth is used for authentication. Google Drive API (scope: drive.file) is used for 
              exporting notes to your personal Google Drive. We do not access other files in your Drive.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;