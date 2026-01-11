// FILE: src/pages/HomePage.jsx
import { Link } from 'react-router-dom';
import { 
  BookOpen, Target, TrendingUp, Users, 
  Brain, FileText, Map, BarChart3, 
  UploadCloud, Mail, Sparkles, Zap,  // ✅ Correct name
  ArrowRight, CheckCircle, Code
} from 'lucide-react';
import { useEffect, useState } from 'react';

const HomePage = () => {
  const [activeFeature, setActiveFeature] = useState(0);

  const modules = [
    {
      icon: BookOpen,
      title: 'Structured Courses',
      description: 'Follow curated courses or create your own learning paths from any source.',
      features: ['Admin-curated courses', 'Personal course creation', 'Progress tracking', 'Resource integration'],
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: FileText,
      title: 'AI-Powered Study Notes',
      description: 'Create comprehensive notes with 4 AI tools and seamless export capabilities.',
      features: ['Generate explanations', 'Improve content', 'Summarize text', 'Export to PDF'],
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Map,
      title: 'Advanced Roadmapper',
      description: 'Build custom learning roadmaps with built-in templates and progress tracking.',
      features: ['Built-in templates', 'Custom roadmaps', 'Progress tracking', 'Milestone management'],
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: BarChart3,
      title: 'Learning Analytics',
      description: 'Visualize your learning journey with detailed analytics and performance insights.',
      features: ['Progress analytics', 'Time tracking', 'Performance metrics', 'Achievement tracking'],
      color: 'from-orange-500 to-red-500'
    }
  ];

  const stats = [
    { value: '10,000+', label: 'Active Learners', icon: Users },
    { value: '500K+', label: 'Notes Created', icon: FileText },
    { value: '50K+', label: 'Roadmaps Built', icon: Map },
    { value: '98%', label: 'Satisfaction Rate', icon: Target }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % modules.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [modules.length]);

  const ActiveIcon = modules[activeFeature].icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Navbar */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-8 h-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">SK-LearnTrack</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-gray-700 hover:text-primary-600 font-medium transition-colors">
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-32 pb-20">
        {/* Animated Background Blobs */}
        <div className="absolute inset-0 z-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>

        <div className="container relative z-10 mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-primary-100 text-primary-600 text-sm font-medium animate-fade-in-up">
              <Sparkles className="w-4 h-4" />
              AI-Powered Learning Platform
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight animate-fade-in-up">
              Master Any Skill with{' '}
              <span className="bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Intelligent Learning
              </span>
            </h1>

            <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto animate-fade-in-up">
              SK-LearnTrack combines AI-powered notes, smart roadmaps, and detailed analytics to help you learn faster and smarter.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up">
              <Link 
                to="/register" 
                className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-primary-600 to-purple-600 rounded-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
              >
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-2 transition-transform" />
              </Link>
              
              <Link 
                to="/login" 
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-gray-700 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-500 hover:text-primary-600 transition-all duration-300"
              >
                View Demo
              </Link>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 animate-fade-in-up">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Effective Learning
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Four powerful modules working together to supercharge your learning journey
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 mb-20">
            {/* Modules List */}
            <div className="space-y-6">
              {modules.map((module, index) => (
                <div
                  key={index}
                  className={`p-6 rounded-2xl border-2 transition-all duration-300 cursor-pointer hover:shadow-xl ${
                    activeFeature === index 
                      ? 'border-primary-500 bg-gradient-to-br from-white to-primary-50 shadow-lg' 
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                  onClick={() => setActiveFeature(index)}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${module.color}`}>
                      <module.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {module.title}
                      </h3>
                      <p className="text-gray-600 mb-3">
                        {module.description}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {module.features.map((feature, idx) => (
                          <span 
                            key={idx}
                            className="inline-flex items-center gap-1 px-3 py-1 text-sm rounded-full bg-gray-100 text-gray-700"
                          >
                            <CheckCircle className="w-3 h-3 text-primary-600" />
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Feature Preview */}
            <div className="relative">
              <div className="sticky top-24 p-8 rounded-3xl bg-gradient-to-br from-gray-900 to-gray-800 text-white h-[500px] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-xl bg-white/10 backdrop-blur-sm">
                      <ActiveIcon className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold">
                      {modules[activeFeature].title}
                    </h3>
                  </div>
                  <p className="text-gray-300 text-lg mb-8">
                    {modules[activeFeature].description}
                  </p>
                  
                  <ul className="space-y-3">
                    {modules[activeFeature].features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-primary-400"></div>
                        <span className="text-gray-300">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <button className="w-full py-4 bg-white text-gray-900 font-semibold rounded-xl hover:bg-gray-100 transition-colors duration-300 flex items-center justify-center gap-2">
                  Explore {modules[activeFeature].title}
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* AI Features Grid */}
          <div className="mt-32">
            <h2 className="text-4xl font-bold text-center text-gray-900 mb-4">
              AI-Powered Learning Tools
            </h2>
            <p className="text-xl text-center text-gray-600 mb-12 max-w-3xl mx-auto">
              Four specialized AI tools integrated into your study notes
            </p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: Brain,
                  title: 'Generate Explanations',
                  description: 'AI creates detailed explanations for complex topics instantly',
                  color: 'bg-gradient-to-br from-blue-500 to-cyan-500'
                },
                {
                  icon: Zap,
                  title: 'Improve Content',
                  description: 'Enhance your writing quality and clarity with AI suggestions',
                  color: 'bg-gradient-to-br from-purple-500 to-pink-500'
                },
                {
                  icon: FileText,
                  title: 'Summarize Text',
                  description: 'Get concise summaries of lengthy study materials',
                  color: 'bg-gradient-to-br from-green-500 to-emerald-500'
                },
                {
                  icon: Code,
                  title: 'Generate Code',
                  description: 'AI creates code snippets in multiple programming languages',
                  color: 'bg-gradient-to-br from-orange-500 to-red-500'
                },
                {
                  icon: Mail,
                  title: 'Daily Reports',
                  description: 'Personalized email summaries of your daily learning progress',
                  color: 'bg-gradient-to-br from-indigo-500 to-purple-500'
                },
              {
                icon: UploadCloud,  // ✅
                title: 'Auto-Sync',
                description: 'Export notes as PDF and sync automatically with Google Drive',
                color: 'bg-gradient-to-br from-pink-500 to-rose-500'
              }
              ].map((feature, index) => (
                <div
                  key={index}
                  className="group relative p-8 rounded-2xl bg-white border border-gray-200 hover:border-primary-500 transition-all duration-300 hover:shadow-2xl"
                >
                  <div className={`inline-flex p-4 rounded-xl ${feature.color} mb-6`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                  <div className="absolute bottom-8 right-8 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <ArrowRight className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-purple-600 to-pink-600"></div>
        
        <div className="container relative z-10 mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-white mb-6">
              Start Your Learning Journey Today
            </h2>
            <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
              Join thousands of learners who are mastering new skills faster with SK-LearnTrack.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/register" 
                className="group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-primary-600 bg-white rounded-xl hover:bg-gray-50 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-2xl"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-2 transition-transform" />
              </Link>
              
              <Link 
                to="/login" 
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border-2 border-white/30 rounded-xl hover:bg-white/10 transition-all duration-300"
              >
                <BookOpen className="mr-2 w-5 h-5" />
                View Demo
              </Link>
            </div>
            
            <p className="mt-8 text-white/70">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-8 h-8 text-primary-400" />
                <span className="text-xl font-bold">SK-LearnTrack</span>
              </div>
              <p className="text-gray-400">
                Your all-in-one platform for mastering any skill with AI-powered tools.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Modules</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/courses" className="hover:text-primary-400 transition-colors">Courses</Link></li>
                <li><Link to="/notes" className="hover:text-primary-400 transition-colors">Study Notes</Link></li>
                <li><Link to="/roadmap" className="hover:text-primary-400 transition-colors">Roadmapper</Link></li>
                <li><Link to="/analytics" className="hover:text-primary-400 transition-colors">Analytics</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li className="flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  <span>AI Tools</span>
                </li>
                <li className="flex items-center gap-2">
                  <UploadCloud className="w-4 h-4" />  // ✅
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
            
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-400">
                <li>support@sklearntrack.com</li>
                <li>+1 (555) 123-4567</li>
                <li>San Francisco, CA</li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} SK-LearnTrack. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;