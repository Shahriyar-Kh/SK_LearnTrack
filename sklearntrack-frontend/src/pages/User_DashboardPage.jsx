// FILE: src/pages/User_DashboardPage.jsx - FULLY DYNAMIC VERSION
// ============================================================================

import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout as logoutAction } from '@/store/slices/authSlice';
import { 
  BookOpen, FileText, Map, TrendingUp, Bell, Settings, User, LogOut, 
  Menu, X, ChevronRight, Flame, Play, PlusCircle, Brain, Code, 
  CheckCircle, Clock, Target, Calendar, Award, Loader2, AlertCircle
} from 'lucide-react';
import { dashboardService } from '@/services/dashboard.service';
import { toast } from 'react-hot-toast';

const DashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dashboard Data (Real + Dummy mixed)
  const [dashboardData, setDashboardData] = useState(null);
  const [recentNotes, setRecentNotes] = useState([]);
  const [quickActions, setQuickActions] = useState([]);
  const [todayPlan, setTodayPlan] = useState([]);
  const [activeCourses, setActiveCourses] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all dashboard data in parallel
      const [overview, notes, actions, plan, courses] = await Promise.all([
        dashboardService.getOverview(),
        dashboardService.getRecentNotes(),
        dashboardService.getQuickActions(),
        dashboardService.getTodayPlan(),
        dashboardService.getActiveCourses() // DUMMY for now
      ]);

      setDashboardData(overview.data);
      setRecentNotes(notes.data || []);
      setQuickActions(actions.data || []);
      setTodayPlan(plan.data || []);
      setActiveCourses(courses.data || []);

    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await dispatch(logoutAction()).unwrap();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed');
    }
  };

  const handleTaskToggle = async (taskId, currentStatus) => {
    try {
      await dashboardService.updateTask(taskId, !currentStatus);
      setTodayPlan(prev => 
        prev.map(task => 
          task.id === taskId 
            ? { ...task, completed: !currentStatus }
            : task
        )
      );
      toast.success('Task updated');
    } catch (error) {
      console.error('Task update error:', error);
      toast.error('Failed to update task');
    }
  };

  const navigationItems = [
    { 
      icon: Target, 
      label: 'Dashboard', 
      path: '/dashboard',
      badge: null
    },
    { 
      icon: BookOpen, 
      label: 'Courses', 
      path: '/courses',
      badge: dashboardData?.active_courses || null
    },
    { 
      icon: FileText, 
      label: 'Notes & Code', 
      path: '/notes',
      badge: dashboardData?.total_notes || null
    },
    { 
      icon: Map, 
      label: 'Roadmaps', 
      path: '/roadmap',
      badge: null
    },
    { 
      icon: TrendingUp, 
      label: 'Analytics', 
      path: '/analytics',
      badge: null
    },
    { 
      icon: Bell, 
      label: 'Notifications', 
      path: '/notifications',
      badge: 3  // DUMMY - Replace with real notification count
    },
  ];

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    return 'bg-orange-500';
  };

  const isActiveRoute = (path) => {
    return location.pathname === path;
  };

  // Loading State
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Error State
  if (error && !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Failed to Load Dashboard</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 lg:relative lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <Link to="/dashboard" className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-900">SK-Learn</span>
              </Link>
              <button onClick={() => setSidebarOpen(false)} className="lg:hidden">
                <X className="w-6 h-6 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigationItems.map((item, idx) => {
              const Icon = item.icon;
              const active = isActiveRoute(item.path);
              return (
                <Link
                  key={idx}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                    active
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${
                      active ? 'bg-white text-blue-600' : 'bg-blue-100 text-blue-600'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold overflow-hidden">
                {dashboardData?.user_avatar ? (
                  <img 
                    src={dashboardData.user_avatar} 
                    alt="Avatar" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  dashboardData?.user_name?.charAt(0) || 'U'
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {dashboardData?.user_name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {dashboardData?.user_email || ''}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Link
                to="/profile"
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center justify-center px-3 py-2 text-sm bg-red-50 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-x-hidden">
        {/* Top Bar */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-4">
              <button onClick={() => setSidebarOpen(true)} className="lg:hidden">
                <Menu className="w-6 h-6 text-gray-700" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {getGreeting()}, {dashboardData?.user_name?.split(' ')[0] || 'there'}! 👋
                </h1>
                <p className="text-sm text-gray-600">Here's your learning progress today</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell className="w-6 h-6 text-gray-700" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <Link 
                to="/profile"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
              >
                <User className="w-6 h-6 text-gray-700" />
              </Link>
            </div>
          </div>
        </header>

        <div className="p-4 md:p-8 space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Clock className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Week</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Study Time</p>
              <p className="text-3xl font-bold">{dashboardData?.weekly_study_time || 0} min</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Flame className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Streak</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Current Streak</p>
              <p className="text-3xl font-bold">{dashboardData?.current_streak || 0} days</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <BookOpen className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Active</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Courses</p>
              <p className="text-3xl font-bold">{dashboardData?.active_courses || 0}</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Target className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Done</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Topics</p>
              <p className="text-3xl font-bold">{dashboardData?.topics_completed || 0}</p>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Active Courses */}
            <div className="lg:col-span-2 space-y-6">
              {/* Courses Section */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Active Courses</h2>
                  <Link 
                    to="/courses"
                    className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
                  >
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>

                {activeCourses.length > 0 ? (
                  <div className="space-y-4">
                    {activeCourses.map((course) => (
                      <div key={course.id} className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-semibold text-gray-900">{course.title}</h3>
                          <span className="text-sm font-bold text-blue-600">{course.progress}%</span>
                        </div>
                        
                        <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
                          <div 
                            className={`absolute left-0 top-0 h-full ${getProgressColor(course.progress)} transition-all`}
                            style={{ width: `${course.progress}%` }}
                          />
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Next: {course.nextLesson}</span>
                          <button className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium">
                            <Play className="w-4 h-4" />
                            Continue
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">No active courses yet</p>
                    <Link
                      to="/courses"
                      className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Browse Courses
                    </Link>
                  </div>
                )}
              </div>

              {/* Recent Notes */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Recent Notes</h2>
                  <Link
                    to="/notes"
                    className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
                  >
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>

                {recentNotes.length > 0 ? (
                  <div className="space-y-3">
                    {recentNotes.map((note) => (
                      <Link
                        key={note.id}
                        to={`/notes?id=${note.id}`}
                        className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <FileText className="w-5 h-5 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">{note.title}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">{note.time_ago}</span>
                            <div className="flex gap-1">
                              {note.tags && note.tags.slice(0, 2).map((tag, idx) => (
                                <span key={idx} className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">No notes yet</p>
                    <Link
                      to="/notes"
                      className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Create First Note
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  {quickActions.map((action) => {
                    const IconComponent = action.icon === 'PlusCircle' ? PlusCircle :
                                         action.icon === 'BookOpen' ? BookOpen :
                                         action.icon === 'Brain' ? Brain :
                                         action.icon === 'Code' ? Code : PlusCircle;
                    
                    return (
                      <Link
                        key={action.id}
                        to={action.route}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                          action.id === 'new-note'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg'
                            : 'bg-gray-100 hover:bg-gray-200'
                        }`}
                      >
                        <IconComponent className={`w-5 h-5 ${action.id === 'new-note' ? '' : 'text-gray-700'}`} />
                        <span className={`font-medium ${action.id === 'new-note' ? '' : 'text-gray-900'}`}>
                          {action.label}
                        </span>
                        {action.badge && (
                          <span className="ml-auto text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full font-bold">
                            {action.badge}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>

              {/* Today's Plan */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Calendar className="w-5 h-5 text-gray-700" />
                  <h2 className="text-lg font-bold text-gray-900">Today's Plan</h2>
                </div>
                <div className="space-y-3">
                  {todayPlan.map((item) => (
                    <div 
                      key={item.id} 
                      onClick={() => handleTaskToggle(item.id, item.completed)}
                      className={`flex items-start gap-3 p-3 rounded-lg transition-colors cursor-pointer ${
                        item.completed ? 'bg-green-50' : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      {item.completed ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      ) : (
                        <div className="w-5 h-5 border-2 border-gray-300 rounded-full mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${item.completed ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                          {item.task}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{item.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Achievement Badge */}
              <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl p-6 text-white">
                <div className="flex items-center justify-between mb-3">
                  <Award className="w-8 h-8" />
                  <span className="text-2xl">🔥</span>
                </div>
                <h3 className="text-lg font-bold mb-2">
                  {dashboardData?.current_streak || 0}-Day Streak!
                </h3>
                <p className="text-sm opacity-90 mb-4">
                  Keep up the amazing work! You're on fire!
                </p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-white/30 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-white rounded-full" 
                      style={{ width: `${Math.min((dashboardData?.current_streak || 0) * 10, 100)}%` }} 
                    />
                  </div>
                  <span className="text-sm font-bold">
                    {dashboardData?.current_streak || 0}/{dashboardData?.longest_streak || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;