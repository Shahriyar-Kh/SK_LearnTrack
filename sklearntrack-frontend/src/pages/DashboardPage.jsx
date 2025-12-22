// FILE: src/pages/DashboardPage.jsx
// ============================================================================

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpen, FileText, Map, TrendingUp, Award, 
  Calendar, Clock, Target 
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import { analyticsService } from '@/services/analytics.service';
import { courseService } from '@/services/course.service';
import { noteService } from '@/services/note.service';

const DashboardPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [recentNotes, setRecentNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsData, enrollmentsData, notesData] = await Promise.all([
        analyticsService.getDashboard(),
        courseService.getEnrollments(),
        noteService.getNotes({ page_size: 5 }),
      ]);

      setAnalytics(analyticsData);
      setEnrollments(enrollmentsData.results || []);
      setRecentNotes(notesData.results || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar />
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {getGreeting()}! 👋
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Here's your learning progress today
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Study Time (Week)</p>
                <h3 className="text-3xl font-bold mt-2">
                  {analytics?.weekly_study_time || 0} min
                </h3>
              </div>
              <Clock size={40} className="text-blue-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Current Streak</p>
                <h3 className="text-3xl font-bold mt-2">
                  {analytics?.current_streak || 0} days
                </h3>
              </div>
              <Award size={40} className="text-green-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Active Courses</p>
                <h3 className="text-3xl font-bold mt-2">
                  {enrollments.length}
                </h3>
              </div>
              <BookOpen size={40} className="text-purple-200" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Topics Completed</p>
                <h3 className="text-3xl font-bold mt-2">
                  {analytics?.topics_completed || 0}
                </h3>
              </div>
              <Target size={40} className="text-orange-200" />
            </div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Active Courses */}
          <div className="lg:col-span-2">
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Active Courses</h2>
                <Link to="/courses" className="text-primary-600 hover:text-primary-700 text-sm">
                  View All →
                </Link>
              </div>
              
              {enrollments.length > 0 ? (
                <div className="space-y-4">
                  {enrollments.slice(0, 3).map((enrollment) => (
                    <Link
                      key={enrollment.id}
                      to={`/courses/${enrollment.course.slug}`}
                      className="block p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{enrollment.course.title}</h3>
                        <span className="text-sm text-primary-600">
                          {enrollment.progress_percentage}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${enrollment.progress_percentage}%` }}
                        />
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    No active courses yet
                  </p>
                  <Link to="/courses" className="btn-primary">
                    Browse Courses
                  </Link>
                </div>
              )}
            </Card>

            {/* Recent Notes */}
            <Card className="mt-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Recent Notes</h2>
                <Link to="/notes" className="text-primary-600 hover:text-primary-700 text-sm">
                  View All →
                </Link>
              </div>
              
              {recentNotes.length > 0 ? (
                <div className="space-y-3">
                  {recentNotes.map((note) => (
                    <Link
                      key={note.id}
                      to={`/notes?id=${note.id}`}
                      className="block p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <FileText size={20} className="text-primary-600" />
                        <div className="flex-1">
                          <h4 className="font-medium">{note.title}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(note.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    No notes yet
                  </p>
                  <Link to="/notes" className="btn-primary">
                    Create Note
                  </Link>
                </div>
              )}
            </Card>
          </div>

          {/* Quick Actions & Study Plan */}
          <div>
            <Card>
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link to="/notes" className="btn-primary w-full flex items-center justify-center gap-2">
                  <FileText size={18} />
                  New Note
                </Link>
                <Link to="/courses" className="btn-secondary w-full flex items-center justify-center gap-2">
                  <BookOpen size={18} />
                  Browse Courses
                </Link>
                <Link to="/roadmap" className="btn-secondary w-full flex items-center justify-center gap-2">
                  <Map size={18} />
                  View Roadmap
                </Link>
                <Link to="/analytics" className="btn-secondary w-full flex items-center justify-center gap-2">
                  <TrendingUp size={18} />
                  Analytics
                </Link>
              </div>
            </Card>

            {/* Today's Plan */}
            <Card className="mt-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Calendar size={20} />
                Today's Plan
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-primary-50 dark:bg-primary-900 rounded-lg">
                  <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                  <p className="text-sm">Review yesterday's notes</p>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <p className="text-sm">Continue active course</p>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <p className="text-sm">Update learning roadmap</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
