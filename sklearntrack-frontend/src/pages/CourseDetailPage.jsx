import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, BookOpen, Award, ChevronRight } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import { courseService } from '@/services/course.service';
import toast from 'react-hot-toast';

const CourseDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolled, setEnrolled] = useState(false);

  useEffect(() => {
    fetchCourseDetail();
  }, [slug]);

  const fetchCourseDetail = async () => {
    try {
      const data = await courseService.getCourseDetail(slug);
      setCourse(data);
    } catch (error) {
      toast.error('Failed to fetch course details');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    try {
      await courseService.enrollCourse(slug);
      setEnrolled(true);
      toast.success('Successfully enrolled!');
    } catch (error) {
      toast.error('Failed to enroll');
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

  if (!course) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navbar />
        <div className="container mx-auto px-4 py-20 text-center">
          <h2 className="text-2xl font-bold mb-4">Course not found</h2>
          <Button onClick={() => navigate('/courses')}>Back to Courses</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card>
              <h1 className="text-3xl font-bold mb-4">{course.title}</h1>
              <p className="text-gray-600 dark:text-gray-400 mb-6">{course.description}</p>

              <div className="flex items-center gap-6 mb-8">
                <div className="flex items-center gap-2">
                  <Clock size={20} className="text-gray-400" />
                  <span>{course.estimated_duration}h</span>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen size={20} className="text-gray-400" />
                  <span>{course.chapters?.length || 0} chapters</span>
                </div>
                <div className="flex items-center gap-2">
                  <Award size={20} className="text-gray-400" />
                  <span className="capitalize">{course.difficulty}</span>
                </div>
              </div>

              {/* Chapters */}
              <div className="space-y-4">
                <h2 className="text-2xl font-bold mb-4">Course Content</h2>
                {course.chapters?.map((chapter, idx) => (
                  <div key={chapter.id} className="border dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">
                          Chapter {idx + 1}: {chapter.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {chapter.topics?.length || 0} topics
                        </p>
                      </div>
                      <ChevronRight className="text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div>
            <Card>
              <h3 className="text-xl font-bold mb-4">Enroll in Course</h3>
              {enrolled ? (
                <div className="text-center py-4">
                  <p className="text-green-600 mb-4">✓ You're enrolled!</p>
                  <Button className="w-full">Continue Learning</Button>
                </div>
              ) : (
                <div>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Start learning now and track your progress
                  </p>
                  <Button onClick={handleEnroll} className="w-full">
                    Enroll Now
                  </Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetailPage;