// FILE: src/pages/PrivacyPolicy.jsx
// ============================================================================

import { Link } from 'react-router-dom';
import { Shield, Lock, Eye, FileText, Mail, ArrowLeft } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-12 pt-24">
        <div className="max-w-4xl mx-auto">
          {/* Back Button */}
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>

          {/* Header */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-primary-100 rounded-xl">
                <Shield className="w-8 h-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
                <p className="text-gray-600">Last Updated: January 13, 2025</p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Lock className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">Our Commitment</h3>
                  <p className="text-blue-700">
                    We collect minimal data and never sell your information. Your privacy is our priority.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Content Sections */}
          <div className="space-y-8">
            {/* Introduction */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 mb-4">
                Welcome to Sk-LearnTrack ("we," "our," or "us"). We are committed to protecting your privacy. 
                This Privacy Policy explains how we collect, use, disclose, and safeguard your information when 
                you use our online learning and note management platform.
              </p>
            </section>

            {/* Information We Collect */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Information We Collect</h2>
              
              <div className="space-y-6">
                <div className="border-l-4 border-primary-500 pl-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Google OAuth Data (When you sign in with Google)</h3>
                  <ul className="text-gray-700 list-disc pl-5 space-y-1">
                    <li>Email address</li>
                    <li>Basic profile information (name, profile picture)</li>
                    <li>Google user ID</li>
                  </ul>
                </div>

                <div className="border-l-4 border-green-500 pl-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Google Drive Data (When you connect Google Drive)</h3>
                  <ul className="text-gray-700 list-disc pl-5 space-y-1">
                    <li>Access to create and manage files in your Google Drive (scope: drive.file)</li>
                    <li>Files you choose to upload or create through our platform</li>
                    <li>We only access files created or opened by Sk-LearnTrack</li>
                  </ul>
                </div>

                <div className="border-l-4 border-blue-500 pl-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Automatically Collected Information</h3>
                  <ul className="text-gray-700 list-disc pl-5 space-y-1">
                    <li>Browser type and version</li>
                    <li>IP address</li>
                    <li>Pages visited and time spent on our platform</li>
                    <li>Cookies and session data for authentication</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Google Drive Integration */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Google Drive Integration</h2>
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-4">
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-yellow-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-yellow-900 mb-2">Important: Limited Access</h3>
                    <p className="text-yellow-700">
                      Our platform uses Google Drive API with the following limitations:
                    </p>
                    <ul className="text-yellow-700 list-disc pl-5 mt-2 space-y-1">
                      <li><strong>Scope: drive.file</strong> - access only to files created by Sk-LearnTrack</li>
                      <li>We <strong>cannot access</strong>, view, or modify other files in your Google Drive</li>
                      <li>All uploaded notes remain in your personal Google Drive account</li>
                      <li>You can <strong>revoke access anytime</strong> via your Google Account settings</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>

            {/* How We Use Your Information */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. How We Use Your Information</h2>
              <p className="text-gray-700 mb-4">
                We use your information solely to:
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center mb-3">
                    <Eye className="w-5 h-5 text-primary-600" />
                  </div>
                  <p className="text-gray-700">Provide and maintain our learning platform</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <p className="text-gray-700">Enable Google Drive integration for note storage</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                    <Lock className="w-5 h-5 text-blue-600" />
                  </div>
                  <p className="text-gray-700">Authenticate your account and ensure security</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                    <Mail className="w-5 h-5 text-purple-600" />
                  </div>
                  <p className="text-gray-700">Communicate important updates and improvements</p>
                </div>
              </div>
            </section>

            {/* Data Storage and Security */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data Storage and Security</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <strong>We do not store your Google Drive files</strong> on our servers. Files remain in your Google Drive.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    Authentication tokens are <strong>encrypted and stored securely</strong>.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    We implement <strong>industry-standard security measures</strong> to protect your data.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    Your data is <strong>never sold or shared</strong> with third parties for marketing.
                  </p>
                </div>
              </div>
            </section>

            {/* User Rights */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Rights and Control</h2>
              <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                <h3 className="font-semibold text-green-900 mb-3">You have the right to:</h3>
                <ul className="text-green-700 space-y-2">
                  <li className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span><strong>Access</strong> your personal information</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span><strong>Correct</strong> inaccurate data</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span><strong>Delete</strong> your account and associated data</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span><strong>Revoke Google Drive access</strong> anytime via Google Account settings</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span><strong>Export</strong> your notes from Google Drive anytime</span>
                  </li>
                </ul>
              </div>
            </section>

            {/* Contact Information */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Contact Information</h2>
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="font-semibold text-gray-900 mb-3">For privacy-related questions or to exercise your rights:</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-primary-600" />
                    <a 
                      href="mailto:shahriyarkhanpk1@gmail.com" 
                      className="text-primary-600 hover:text-primary-700"
                    >
                      shahriyarkhanpk1@gmail.com
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-primary-600" />
                    <a 
                      href="https://sk-learntrack.vercel.app" 
                      className="text-primary-600 hover:text-primary-700"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      https://sk-learntrack.vercel.app
                    </a>
                  </div>
                </div>
              </div>
            </section>

            {/* Policy Updates */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Policy Updates</h2>
              <p className="text-gray-700">
                We may update this Privacy Policy periodically. We will notify you of significant changes via 
                email or platform notification. The "Last Updated" date at the top indicates when this policy 
                was last revised.
              </p>
            </section>
          </div>

          {/* Footer Note */}
          <div className="mt-12 p-6 bg-gray-900 text-white rounded-2xl">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="w-6 h-6 text-primary-400" />
              <h3 className="text-lg font-semibold">Your Privacy Matters</h3>
            </div>
            <p className="text-gray-300">
              This policy is designed to be transparent and easy to understand. If you have any questions, 
              please don't hesitate to contact us.
            </p>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default PrivacyPolicy;