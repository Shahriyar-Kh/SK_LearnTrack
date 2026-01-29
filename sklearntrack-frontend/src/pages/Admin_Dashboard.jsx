import { useState } from 'react';
import {
  Users, BookOpen, FileText, Activity, Search, ChevronRight, Eye, Edit, Trash2,
  Download, AlertCircle, CheckCircle, Clock, Award, BarChart3,
  UserPlus, BookPlus, MessageSquare, Shield, Settings
} from 'lucide-react';

const AdminDashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const [stats] = useState({
    totalUsers: 15234,
    totalCourses: 342,
    totalNotes: 52341,
    activeUsers: 8456,
    newUsersToday: 234,
    activeCourses: 89,
    pendingReviews: 12,
    systemHealth: 98,
  });

  const [recentUsers] = useState([
    { id: 1, name: 'John Doe', email: 'john@example.com', joined: '2 hours ago', status: 'active', courses: 5 },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', joined: '5 hours ago', status: 'active', courses: 3 },
    { id: 3, name: 'Mike Johnson', email: 'mike@example.com', joined: '1 day ago', status: 'inactive', courses: 2 },
    { id: 4, name: 'Sarah Williams', email: 'sarah@example.com', joined: '2 days ago', status: 'active', courses: 7 },
  ]);

  const [topCourses] = useState([
    { id: 1, title: 'Machine Learning Fundamentals', students: 1234, completion: 78, rating: 4.8 },
    { id: 2, title: 'Web Development Bootcamp', students: 2341, completion: 82, rating: 4.9 },
    { id: 3, title: 'Data Science with Python', students: 1567, completion: 71, rating: 4.7 },
    { id: 4, title: 'Mobile App Development', students: 987, completion: 65, rating: 4.6 },
  ]);

  const [announcements] = useState([
    { id: 1, title: 'System Maintenance Scheduled', date: '2 hours ago', priority: 'high' },
    { id: 2, title: 'New Features Released', date: '1 day ago', priority: 'medium' },
    { id: 3, title: 'Weekly Report Available', date: '2 days ago', priority: 'low' },
  ]);

  const navigationItems = [
    { icon: Activity, label: 'Dashboard', active: true },
    { icon: Users, label: 'User Management', badge: '15.2K' },
    { icon: BookOpen, label: 'Course Management', badge: '342' },
    { icon: FileText, label: 'Content Review', badge: 12 },
    { icon: MessageSquare, label: 'Announcements' },
    { icon: BarChart3, label: 'Analytics' },
    { icon: Settings, label: 'Settings' },
  ];

  const getStatusColor = (status) => {
    return status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600';
  };

  const getPriorityColor = (priority) => {
    if (priority === 'high') return 'bg-red-100 text-red-700';
    if (priority === 'medium') return 'bg-yellow-100 text-yellow-700';
    return 'bg-blue-100 text-blue-700';
  };

  return (
    <div className="p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          <p className="text-sm text-gray-300">Platform overview and quick actions</p>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search users, courses, content..."
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder:text-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        </div>

        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-xl">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-3xl font-bold mb-1">Welcome back, Admin! 👋</h1>
            <p className="text-blue-100">Here's what's happening with your platform today</p>
          </div>
        </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-xl">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +12.5%
            </span>
          </div>
          <h3 className="text-gray-600 text-sm mb-1">Total Users</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">+{stats.newUsersToday} today</p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-xl">
              <BookOpen className="w-6 h-6 text-purple-600" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +8.2%
            </span>
          </div>
          <h3 className="text-gray-600 text-sm mb-1">Total Courses</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.totalCourses}</p>
          <p className="text-xs text-gray-500 mt-2">{stats.activeCourses} active</p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-xl">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +24.1%
            </span>
          </div>
          <h3 className="text-gray-600 text-sm mb-1">Total Notes</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.totalNotes.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">Created by users</p>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-xl">
              <Activity className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +5.7%
            </span>
          </div>
          <h3 className="text-gray-600 text-sm mb-1">Active Users</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.activeUsers.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">Last 7 days</p>
        </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Recent Users */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Recent Users</h2>
                <p className="text-sm text-gray-600 mt-1">New registrations and activity</p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <UserPlus className="w-4 h-4" />
                Add User
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">User</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Joined</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Courses</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentUsers.map((user) => (
                    <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium text-gray-900">{user.name}</p>
                          <p className="text-xs text-gray-500">{user.email}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{user.joined}</td>
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">{user.courses}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(user.status)}`}>
                          <div className={`w-1.5 h-1.5 rounded-full ${user.status === 'active' ? 'bg-green-600' : 'bg-gray-400'}`} />
                          {user.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <button className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors" title="View">
                            <Eye className="w-4 h-4 text-gray-600" />
                          </button>
                          <button className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors" title="Edit">
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button className="p-1.5 hover:bg-red-100 rounded-lg transition-colors" title="Delete">
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-gray-600">Showing 4 of {stats.totalUsers.toLocaleString()} users</p>
              <button className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium">
                View All Users
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* System Health */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">System Health</h3>
                  <p className="text-xs text-gray-600">All systems operational</p>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">Overall Health</span>
                    <span className="text-sm font-bold text-green-600">{stats.systemHealth}%</span>
                  </div>
                  <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-500 to-green-600" style={{ width: `${stats.systemHealth}%` }} />
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">API Response</span>
                    <span className="text-green-600 font-medium">Fast</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Database</span>
                    <span className="text-green-600 font-medium">Healthy</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Storage</span>
                    <span className="text-yellow-600 font-medium">67% Used</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Announcements */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-gray-900">Announcements</h3>
                <button className="text-blue-600 hover:text-blue-700">
                  <MessageSquare className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                {announcements.map((announcement) => (
                  <div key={announcement.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{announcement.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Clock className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">{announcement.date}</span>
                        </div>
                      </div>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getPriorityColor(announcement.priority)}`}>
                        {announcement.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full mt-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                View All Announcements
              </button>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-6 text-white">
              <h3 className="font-bold mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button className="w-full flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
                  <Download className="w-4 h-4" />
                  <span className="text-sm font-medium">Export Reports</span>
                </button>
                <button className="w-full flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
                  <BookPlus className="w-4 h-4" />
                  <span className="text-sm font-medium">Create Course</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Top Courses */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Top Performing Courses</h2>
              <p className="text-sm text-gray-600 mt-1">Most popular courses by enrollment</p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Export CSV</span>
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {topCourses.map((course) => (
              <div key={course.id} className="p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 flex-1">{course.title}</h3>
                  <div className="flex items-center gap-1 text-yellow-500">
                    <Award className="w-4 h-4" />
                    <span className="text-sm font-bold">{course.rating}</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Students</p>
                    <p className="text-lg font-bold text-gray-900">{course.students}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Completion</p>
                    <p className="text-lg font-bold text-gray-900">{course.completion}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Rating</p>
                    <p className="text-lg font-bold text-gray-900">{course.rating}/5</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">
                    <Eye className="w-4 h-4" />
                    View
                  </button>
                  <button className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium">
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

  );
};

export default AdminDashboard;