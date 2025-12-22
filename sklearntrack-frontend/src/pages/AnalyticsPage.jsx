import { useEffect, useState } from 'react';
import { TrendingUp, Award, Clock, Target } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import { analyticsService } from '@/services/analytics.service';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [studyHistory, setStudyHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [dashboardData, historyData] = await Promise.all([
        analyticsService.getDashboard(),
        analyticsService.getStudyHistory(30),
      ]);
      setAnalytics(dashboardData);
      setStudyHistory(historyData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar />
        <div className="flex items-center justify-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Learning Analytics
        </h1>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Weekly Study Time</p>
                <h3 className="text-2xl font-bold">{analytics?.weekly_study_time || 0} min</h3>
              </div>
              <Clock size={32} className="text-primary-600" />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Current Streak</p>
                <h3 className="text-2xl font-bold">{analytics?.current_streak || 0} days</h3>
              </div>
              <Award size={32} className="text-green-600" />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Topics Completed</p>
                <h3 className="text-2xl font-bold">{analytics?.topics_completed || 0}</h3>
              </div>
              <Target size={32} className="text-purple-600" />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 dark:text-gray-400 text-sm">Study Sessions</p>
                <h3 className="text-2xl font-bold">{analytics?.study_sessions || 0}</h3>
              </div>
              <TrendingUp size={32} className="text-orange-600" />
            </div>
          </Card>
        </div>

        {/* Study History Chart */}
        <Card>
          <h2 className="text-xl font-bold mb-6">Study Time (Last 30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={studyHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="duration" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsPage;