// FILE: src/pages/TermsOfService.jsx
// ============================================================================

import { Link } from 'react-router-dom';
import { Scale, AlertTriangle, CheckCircle, FileText, Mail, ArrowLeft } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

const TermsOfService = () => {
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
                <Scale className="w-8 h-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Terms of Service</h1>
                <p className="text-gray-600">Last Updated: January 13, 2025 | Effective Date: January 13, 2025</p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">Please Read Carefully</h3>
                  <p className="text-blue-700">
                    By accessing or using Sk-LearnTrack, you agree to be bound by these Terms of Service. 
                    If you disagree with any part, you may not use our services.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Summary */}
          <div className="mb-12 p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl border border-primary-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Summary</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">You own your notes and data</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">No data sharing with third parties</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">Cancel anytime, no hidden fees</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <span className="text-gray-700">Google Drive access is limited</span>
              </div>
            </div>
          </div>

          {/* Content Sections */}
          <div className="space-y-8">
            {/* Acceptance of Terms */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700">
                By accessing or using Sk-LearnTrack ("Service"), you agree to be bound by these Terms of Service. 
                If you disagree with any part of these terms, you may not access the Service.
              </p>
            </section>

            {/* Description of Service */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Description of Service</h2>
              <p className="text-gray-700 mb-4">
                Sk-LearnTrack is an online learning and note management platform that allows users to:
              </p>
              <ul className="text-gray-700 list-disc pl-5 space-y-2">
                <li>Create and organize study notes</li>
                <li>Connect Google Drive for note storage</li>
                <li>Manage personal learning materials</li>
                <li>Access educational tools and features</li>
                <li>Export notes to PDF format</li>
                <li>Use AI-powered study assistance</li>
              </ul>
            </section>

            {/* User Accounts */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Accounts</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <strong>Age Requirement:</strong> You must be at least 13 years old to use our service.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <strong>Account Security:</strong> You are responsible for maintaining the confidentiality 
                    of your account credentials and for all activities that occur under your account.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <strong>Authentication:</strong> You may use Google OAuth for authentication. We only collect 
                    minimal information necessary for account creation and authentication.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                  <p className="text-gray-700">
                    <strong>Accuracy:</strong> You must provide accurate, current, and complete information 
                    during registration and keep it updated.
                  </p>
                </div>
              </div>
            </section>

            {/* Acceptable Use */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Acceptable Use</h2>
              <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-4">
                <h3 className="font-semibold text-red-900 mb-3">You agree NOT to:</h3>
                <ul className="text-red-700 space-y-2">
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>Violate any applicable laws, regulations, or third-party rights</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>Infringe upon intellectual property rights of others</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>Attempt to compromise platform security or access unauthorized areas</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>Use the service for illegal activities or harassment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>Overload or disrupt our infrastructure with excessive requests</span>
                  </li>
                </ul>
              </div>
            </section>

            {/* Google Drive Integration */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Google Drive Integration</h2>
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                <h3 className="font-semibold text-yellow-900 mb-3">Important Limitations</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-yellow-700">
                      <strong>You control access:</strong> You decide which files we can access
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-yellow-700">
                      <strong>Limited scope:</strong> We only interact with files you explicitly create or 
                      upload through Sk-LearnTrack (scope: drive.file)
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-yellow-700">
                      <strong>Revocable access:</strong> You can disconnect Google Drive anytime via your 
                      Google Account settings
                    </p>
                  </div>
                  <div className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-yellow-700">
                      <strong>No liability:</strong> We are not responsible for Google Drive service 
                      interruptions or data loss on third-party services
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Intellectual Property */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Intellectual Property</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-green-50 rounded-xl p-6">
                  <h3 className="font-semibold text-green-900 mb-3">Your Content</h3>
                  <ul className="text-green-700 space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>You retain full ownership of your notes and content</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>You can export and download your data anytime</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>No claim of ownership by Sk-LearnTrack</span>
                    </li>
                  </ul>
                </div>
                <div className="bg-blue-50 rounded-xl p-6">
                  <h3 className="font-semibold text-blue-900 mb-3">Our Platform</h3>
                  <ul className="text-blue-700 space-y-2">
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>We retain ownership of our platform, code, and design</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>License required for using our service</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>All trademarks and logos are our property</span>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Limitation of Liability */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Limitation of Liability</h2>
              <div className="bg-gray-50 rounded-xl p-6">
                <p className="text-gray-700 mb-4">
                  Sk-LearnTrack is provided "as is" without warranties of any kind, either express or implied. 
                  To the fullest extent permitted by law:
                </p>
                <ul className="text-gray-700 space-y-2">
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    <span>We are not liable for data loss or corruption</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    <span>We are not liable for service interruptions or downtime</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    <span>We are not liable for third-party service issues (including Google Drive)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    <span>We are not liable for indirect or consequential damages</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                    <span>Maximum liability is limited to fees paid for our service</span>
                  </li>
                </ul>
              </div>
            </section>

            {/* Account Termination */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Account Termination</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-red-50 rounded-xl p-6">
                  <h3 className="font-semibold text-red-900 mb-3">We May Suspend or Terminate Accounts That:</h3>
                  <ul className="text-red-700 space-y-2">
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />
                      <span>Violate these terms</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />
                      <span>Engage in illegal activities</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />
                      <span>Compromise platform security</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />
                      <span>Create excessive burden on our systems</span>
                    </li>
                  </ul>
                </div>
                <div className="bg-green-50 rounded-xl p-6">
                  <h3 className="font-semibold text-green-900 mb-3">Your Rights:</h3>
                  <ul className="text-green-700 space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Delete your account anytime through platform settings</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Export your data before account deletion</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Revoke Google Drive access via Google settings</span>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Contact Information */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Contact Information</h2>
              <div className="bg-primary-50 rounded-xl p-6">
                <h3 className="font-semibold text-primary-900 mb-3">For questions about these Terms of Service:</h3>
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

            {/* Changes to Terms */}
            <section className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Changes to Terms</h2>
              <p className="text-gray-700 mb-4">
                We reserve the right to modify these terms at any time. We will notify users of significant 
                changes via email or platform notification.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                <p className="text-yellow-700">
                  <strong>Continued use</strong> of Sk-LearnTrack after changes constitutes acceptance of 
                  the modified terms.
                </p>
              </div>
            </section>
          </div>

          {/* Disclaimer */}
          <div className="mt-12 p-6 bg-gray-900 text-white rounded-2xl">
            <div className="flex items-center gap-3 mb-3">
              <Scale className="w-6 h-6 text-primary-400" />
              <h3 className="text-lg font-semibold">Legal Disclaimer</h3>
            </div>
            <p className="text-gray-300 mb-2">
              These terms are provided for informational purposes and do not constitute legal advice. 
              Consult with a legal professional to ensure compliance with specific regulations in your jurisdiction.
            </p>
            <p className="text-gray-400 text-sm">
              For Google OAuth compliance, these terms cover required sections including data usage, 
              user rights, and Google Drive integration limitations.
            </p>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default TermsOfService;