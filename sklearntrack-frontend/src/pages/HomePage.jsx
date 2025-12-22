// FILE: src/pages/HomePage.jsx
// ============================================================================

import { Link } from 'react-router-dom';
import { BookOpen, Target, TrendingUp, Users } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';

const HomePage = () => {
  const features = [
    {
      icon: BookOpen,
      title: 'Structured Learning',
      description: 'Follow curated courses or create your own learning paths from any source.',
    },
    {
      icon: Target,
      title: 'Goal Tracking',
      description: 'Set learning goals, create roadmaps, and track your progress every day.',
    },
    {
      icon: TrendingUp,
      title: 'Analytics',
      description: 'Visualize your learning journey with detailed analytics and insights.',
    },
    {
      icon: Users,
      title: 'Personal & Public',
      description: 'Learn from admin courses or create personal courses from any resource.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <Navbar />
      
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Your Personal Learning
            <span className="text-primary-600"> Journey Starts Here</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Track your learning from any source. Create roadmaps. Take notes. 
            Build your knowledge vault. All in one place.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/register" className="btn-primary text-lg px-8 py-3">
              Get Started Free
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-20">
          {features.map((feature, index) => (
            <div key={index} className="card text-center">
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <feature.icon className="text-primary-600" size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;

