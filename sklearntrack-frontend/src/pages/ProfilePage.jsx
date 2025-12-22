import { useState } from 'react';
import { User, Mail, MapPin, BookOpen } from 'lucide-react';
import { useSelector } from 'react-redux';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import { authService } from '@/services/auth.service';
import toast from 'react-hot-toast';

const ProfilePage = () => {
  const { user } = useSelector((state) => state.auth);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    bio: user?.profile?.bio || '',
    skill_interests: user?.profile?.skill_interests || [],
  });

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authService.updateProfile(formData);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Profile Settings
        </h1>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Info */}
          <Card>
            <div className="text-center">
              <div className="w-24 h-24 bg-primary-600 rounded-full flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <h2 className="text-2xl font-bold">{user?.full_name}</h2>
              <p className="text-gray-600 dark:text-gray-400">{user?.email}</p>
            </div>

            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <MapPin size={18} className="text-gray-400" />
                <span>{user?.country}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <BookOpen size={18} className="text-gray-400" />
                <span>{user?.field_of_study}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <User size={18} className="text-gray-400" />
                <span>{user?.education_level}</span>
              </div>
            </div>
          </Card>

          {/* Edit Profile */}
          <div className="lg:col-span-2">
            <Card>
              <h3 className="text-xl font-bold mb-6">Edit Profile</h3>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Bio</label>
                  <textarea
                    value={formData.bio}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    className="input-field min-h-[100px]"
                    placeholder="Tell us about yourself..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Learning Goal</label>
                  <p className="text-gray-600 dark:text-gray-400">{user?.learning_goal}</p>
                </div>

                <Button type="submit" loading={loading}>
                  Save Changes
                </Button>
              </form>
            </Card>

            {/* Stats Card */}
            <Card className="mt-6">
              <h3 className="text-xl font-bold mb-4">Learning Stats</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary-600">
                    {user?.profile?.total_study_days || 0}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Study Days</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {user?.profile?.current_streak || 0}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Current Streak</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-orange-600">
                    {user?.profile?.longest_streak || 0}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Best Streak</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;