import { useState } from 'react';
import { User, Mail, MapPin, BookOpen, Globe, Clock, Target, Bell, Lock, Camera, Save, X, Calendar, TrendingUp, FileText, Award } from 'lucide-react';

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [showImageCrop, setShowImageCrop] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  
  // Mock user data
  const [userData, setUserData] = useState({
    fullName: 'John Doe',
    email: 'john.doe@example.com',
    country: 'United States',
    educationLevel: 'undergraduate',
    fieldOfStudy: 'Computer Science',
    bio: 'Passionate about AI and machine learning. Always eager to learn new technologies.',
    learningGoal: 'Master full-stack development and machine learning',
    preferredStudyHours: 3,
    timezone: 'America/New_York',
    avatar: null,
    skillInterests: ['Python', 'React', 'Machine Learning', 'Data Science'],
  });

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    weeklySummary: true,
    courseReminders: true,
  });

  const [stats] = useState({
    totalStudyDays: 45,
    totalNotes: 123,
    activeCourses: 5,
    lastLogin: '2 hours ago',
    accountCreated: 'January 15, 2024',
    emailVerified: true,
    currentStreak: 7,
    longestStreak: 14,
  });

  const tabs = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'preferences', label: 'Study Preferences', icon: Target },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'activity', label: 'Account Activity', icon: TrendingUp },
  ];

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        setShowImageCrop(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfile = () => {
    setIsEditing(false);
    // API call to save profile
    console.log('Saving profile:', userData);
  };

  const educationLevels = [
    { value: 'high_school', label: 'High School' },
    { value: 'undergraduate', label: 'Undergraduate' },
    { value: 'graduate', label: 'Graduate' },
    { value: 'postgraduate', label: 'Postgraduate' },
    { value: 'professional', label: 'Professional' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Settings</h1>
          <p className="text-gray-600">Manage your account settings and preferences</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Sidebar - Profile Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-8">
              {/* Avatar Section */}
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="w-32 h-32 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-4xl font-bold mx-auto mb-4 overflow-hidden">
                    {userData.avatar ? (
                      <img src={userData.avatar} alt="Profile" className="w-full h-full object-cover" />
                    ) : (
                      userData.fullName.charAt(0)
                    )}
                  </div>
                  <button
                    onClick={() => document.getElementById('avatar-upload').click()}
                    className="absolute bottom-4 right-0 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                  >
                    <Camera className="w-4 h-4" />
                  </button>
                  <input
                    id="avatar-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </div>
                <h2 className="text-xl font-bold text-gray-900">{userData.fullName}</h2>
                <p className="text-gray-600 text-sm">{userData.email}</p>
                {stats.emailVerified && (
                  <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    <Award className="w-3 h-3" />
                    Verified
                  </span>
                )}
              </div>

              {/* Quick Stats */}
              <div className="space-y-3 border-t pt-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Study Days</span>
                  <span className="font-bold text-gray-900">{stats.totalStudyDays}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Current Streak</span>
                  <span className="font-bold text-orange-600">{stats.currentStreak} days</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Notes</span>
                  <span className="font-bold text-gray-900">{stats.totalNotes}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Courses</span>
                  <span className="font-bold text-gray-900">{stats.activeCourses}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Tabs */}
            <div className="bg-white rounded-2xl shadow-lg mb-6 overflow-hidden">
              <div className="flex overflow-x-auto border-b">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                        activeTab === tab.id
                          ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tab Content */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              {/* Personal Info Tab */}
              {activeTab === 'personal' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-gray-900">Personal Information</h3>
                    {!isEditing ? (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Edit Profile
                      </button>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={handleSaveProfile}
                          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Save className="w-4 h-4" />
                          Save Changes
                        </button>
                        <button
                          onClick={() => setIsEditing(false)}
                          className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                        >
                          <X className="w-4 h-4" />
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={userData.fullName}
                          onChange={(e) => setUserData({ ...userData, fullName: e.target.value })}
                          disabled={!isEditing}
                          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          value={userData.email}
                          disabled
                          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-lg bg-gray-50 cursor-not-allowed"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={userData.country}
                          onChange={(e) => setUserData({ ...userData, country: e.target.value })}
                          disabled={!isEditing}
                          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Education Level</label>
                      <select
                        value={userData.educationLevel}
                        onChange={(e) => setUserData({ ...userData, educationLevel: e.target.value })}
                        disabled={!isEditing}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                      >
                        {educationLevels.map((level) => (
                          <option key={level.value} value={level.value}>
                            {level.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Field of Study</label>
                      <div className="relative">
                        <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={userData.fieldOfStudy}
                          onChange={(e) => setUserData({ ...userData, fieldOfStudy: e.target.value })}
                          disabled={!isEditing}
                          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                        />
                      </div>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                      <textarea
                        value={userData.bio}
                        onChange={(e) => setUserData({ ...userData, bio: e.target.value })}
                        disabled={!isEditing}
                        rows={4}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                        placeholder="Tell us about yourself..."
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Study Preferences Tab */}
              {activeTab === 'preferences' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Study Preferences</h3>
                  
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Learning Goal</label>
                      <textarea
                        value={userData.learningGoal}
                        onChange={(e) => setUserData({ ...userData, learningGoal: e.target.value })}
                        rows={3}
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="What do you want to achieve?"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Preferred Study Hours per Day: {userData.preferredStudyHours} hours
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="8"
                        value={userData.preferredStudyHours}
                        onChange={(e) => setUserData({ ...userData, preferredStudyHours: parseInt(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>1 hour</span>
                        <span>8 hours</span>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                      <div className="relative">
                        <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <select
                          value={userData.timezone}
                          onChange={(e) => setUserData({ ...userData, timezone: e.target.value })}
                          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="America/New_York">Eastern Time (ET)</option>
                          <option value="America/Chicago">Central Time (CT)</option>
                          <option value="America/Denver">Mountain Time (MT)</option>
                          <option value="America/Los_Angeles">Pacific Time (PT)</option>
                          <option value="UTC">UTC</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-3">Skill Interests</label>
                      <div className="flex flex-wrap gap-2">
                        {userData.skillInterests.map((skill, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                          >
                            {skill}
                            <button className="hover:text-blue-900">
                              <X className="w-4 h-4" />
                            </button>
                          </span>
                        ))}
                        <button className="px-4 py-2 border-2 border-dashed border-gray-300 rounded-full text-sm text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors">
                          + Add Skill
                        </button>
                      </div>
                    </div>

                    <button className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                      <Save className="w-5 h-5" />
                      Save Preferences
                    </button>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Notification Settings</h3>
                  
                  <div className="space-y-6">
                    {Object.entries(notifications).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {key === 'emailNotifications' && 'Receive email notifications for important updates'}
                            {key === 'weeklySummary' && 'Get a weekly summary of your learning progress'}
                            {key === 'courseReminders' && 'Receive reminders about your active courses'}
                          </p>
                        </div>
                        <button
                          onClick={() => setNotifications({ ...notifications, [key]: !value })}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            value ? 'bg-blue-600' : 'bg-gray-300'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              value ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Security Settings</h3>
                  
                  <div className="space-y-6">
                    <div className="p-6 border border-gray-200 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-4">Change Password</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                          <input
                            type="password"
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="••••••••"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                          <input
                            type="password"
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="••••••••"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                          <input
                            type="password"
                            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="••••••••"
                          />
                        </div>
                        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                          Update Password
                        </button>
                      </div>
                    </div>

                    <div className="p-6 border border-gray-200 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-2">Two-Factor Authentication</h4>
                      <p className="text-sm text-gray-600 mb-4">Add an extra layer of security to your account</p>
                      <button className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors">
                        Enable 2FA
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Account Activity Tab */}
              {activeTab === 'activity' && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Account Activity</h3>
                  
                  <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-blue-600 font-medium">Total Study Days</span>
                        <Calendar className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="text-3xl font-bold text-blue-900">{stats.totalStudyDays}</div>
                    </div>

                    <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-purple-600 font-medium">Total Notes</span>
                        <FileText className="w-5 h-5 text-purple-600" />
                      </div>
                      <div className="text-3xl font-bold text-purple-900">{stats.totalNotes}</div>
                    </div>

                    <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-green-600 font-medium">Active Courses</span>
                        <BookOpen className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="text-3xl font-bold text-green-900">{stats.activeCourses}</div>
                    </div>

                    <div className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-orange-600 font-medium">Best Streak</span>
                        <Award className="w-5 h-5 text-orange-600" />
                      </div>
                      <div className="text-3xl font-bold text-orange-900">{stats.longestStreak} days</div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-700">Last Login</span>
                      <span className="font-medium text-gray-900">{stats.lastLogin}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-700">Account Created</span>
                      <span className="font-medium text-gray-900">{stats.accountCreated}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-700">Email Status</span>
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        <Award className="w-4 h-4" />
                        Verified
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Image Crop Modal (Placeholder) */}
      {showImageCrop && selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Crop Profile Picture</h3>
            <div className="mb-4">
              <img src={selectedImage} alt="Preview" className="w-full rounded-lg" />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setUserData({ ...userData, avatar: selectedImage });
                  setShowImageCrop(false);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save
              </button>
              <button
                onClick={() => setShowImageCrop(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;