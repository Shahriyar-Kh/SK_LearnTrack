import { useState } from 'react';
import { 
  BookOpen, FileText, Map, TrendingUp, Award, Calendar, Clock, Target, 
  Bell, Settings, User, LogOut, Menu, X, ChevronRight, Flame, Star,
  Play, PlusCircle, Brain, Code, CheckCircle, AlertCircle
} from 'lucide-react';

const DashboardPage = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user] = useState({
    name: 'John Doe',
    email: 'shary@example.com',
    avatar: null,
    streak: 7,
  });

  const [stats] = useState({
    weeklyStudyTime: 245,
    currentStreak: 7,
    activeCourses: 5,
    topicsCompleted: 23,
    totalNotes: 45,
    achievements: 12,
  });

  const [activeCourses] = useState([
    { id: 1, title: 'Machine Learning Fundamentals', progress: 65, nextLesson: 'Neural Networks Basics', color: 'blue' },
    { id: 2, title: 'Web Development Bootcamp', progress: 82, nextLesson: 'React Hooks', color: 'purple' },
    { id: 3, title: 'Data Structures & Algorithms', progress: 45, nextLesson: 'Binary Trees', color: 'green' },
  ]);

  const [recentNotes] = useState([
    { id: 1, title: 'Neural Network Notes', date: '2 hours ago', tags: ['AI', 'ML'] },
    { id: 2, title: 'React Hooks Cheatsheet', date: '5 hours ago', tags: ['Web Dev', 'React'] },
    { id: 3, title: 'Algorithm Complexity Analysis', date: '1 day ago', tags: ['CS', 'Algorithms'] },
  ]);

  const [todaysPlan] = useState([
    { id: 1, task: 'Complete ML Assignment', completed: true, time: '9:00 AM' },
    { id: 2, task: 'Review React Hooks', completed: true, time: '11:00 AM' },
    { id: 3, task: 'Practice coding problems', completed: false, time: '2:00 PM' },
    { id: 4, task: 'Update learning roadmap', completed: false, time: '4:00 PM' },
  ]);

  const navigationItems = [
    { icon: Target, label: 'Dashboard', active: true, path: '/dashboard' },
    { icon: BookOpen, label: 'Courses', path: '/courses', badge: 5 },
    { icon: FileText, label: 'Notes & Code', path: '/notes', badge: 45 },
    { icon: Map, label: 'Roadmaps', path: '/roadmaps' },
    { icon: TrendingUp, label: 'Analytics', path: '/analytics' },
    { icon: Bell, label: 'Notifications', path: '/notifications', badge: 3 },
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
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-900">SK-Learn</span>
              </div>
              <button onClick={() => setSidebarOpen(false)} className="lg:hidden">
                <X className="w-6 h-6 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigationItems.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors ${
                    item.active
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
                      item.active ? 'bg-white text-blue-600' : 'bg-blue-100 text-blue-600'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                {user.name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
              <button className="flex items-center justify-center px-3 py-2 text-sm bg-red-50 text-red-600 hover:bg-red-100 rounded-lg transition-colors">
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
                <h1 className="text-2xl font-bold text-gray-900">{getGreeting()}! 👋</h1>
                <p className="text-sm text-gray-600">Here's your learning progress today</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell className="w-6 h-6 text-gray-700" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors lg:hidden">
                <User className="w-6 h-6 text-gray-700" />
              </button>
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
              <p className="text-3xl font-bold">{stats.weeklyStudyTime} min</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Flame className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Streak</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Current Streak</p>
              <p className="text-3xl font-bold">{stats.currentStreak} days</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <BookOpen className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Active</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Courses</p>
              <p className="text-3xl font-bold">{stats.activeCourses}</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white">
              <div className="flex items-center justify-between mb-3">
                <Target className="w-8 h-8 opacity-80" />
                <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded-full">Done</span>
              </div>
              <p className="text-sm opacity-90 mb-1">Topics</p>
              <p className="text-3xl font-bold">{stats.topicsCompleted}</p>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Active Courses */}
            <div className="lg:col-span-2 space-y-6">
              {/* Courses Section */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Active Courses</h2>
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

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
              </div>

              {/* Recent Notes */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Recent Notes</h2>
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-3">
                  {recentNotes.map((note) => (
                    <div key={note.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">{note.title}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500">{note.date}</span>
                          <div className="flex gap-1">
                            {note.tags.map((tag, idx) => (
                              <span key={idx} className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
                <div className="space-y-3">
                  <button className="w-full flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all">
                    <PlusCircle className="w-5 h-5" />
                    <span className="font-medium">New Note</span>
                  </button>
                  <button className="w-full flex items-center gap-3 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors">
                    <BookOpen className="w-5 h-5 text-gray-700" />
                    <span className="font-medium text-gray-900">Browse Courses</span>
                  </button>
                  <button className="w-full flex items-center gap-3 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors">
                    <Brain className="w-5 h-5 text-gray-700" />
                    <span className="font-medium text-gray-900">AI Assistant</span>
                  </button>
                  <button className="w-full flex items-center gap-3 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors">
                    <Code className="w-5 h-5 text-gray-700" />
                    <span className="font-medium text-gray-900">Code Vault</span>
                  </button>
                </div>
              </div>

              {/* Today's Plan */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Calendar className="w-5 h-5 text-gray-700" />
                  <h2 className="text-lg font-bold text-gray-900">Today's Plan</h2>
                </div>
                <div className="space-y-3">
                  {todaysPlan.map((item) => (
                    <div key={item.id} className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                      item.completed ? 'bg-green-50' : 'bg-gray-50 hover:bg-gray-100'
                    }`}>
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
                  <Star className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold mb-2">7-Day Streak!</h3>
                <p className="text-sm opacity-90 mb-4">
                  Keep up the amazing work! You're on fire! 🔥
                </p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-white/30 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full" style={{ width: '70%' }} />
                  </div>
                  <span className="text-sm font-bold">7/10</span>
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