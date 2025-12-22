import { useEffect, useState } from 'react';
import { Plus, CheckCircle, Circle } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import { roadmapService } from '@/services/roadmap.service';
import toast from 'react-hot-toast';

const RoadmapPage = () => {
  const [roadmaps, setRoadmaps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  const fetchRoadmaps = async () => {
    try {
      const data = await roadmapService.getRoadmaps();
      setRoadmaps(data.results || []);
    } catch (error) {
      toast.error('Failed to fetch roadmaps');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Learning Roadmaps
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Plan your learning journey and track progress
            </p>
          </div>
          <Button>
            <Plus size={20} className="mr-2" />
            New Roadmap
          </Button>
        </div>

        {roadmaps.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {roadmaps.map((roadmap) => (
              <Card key={roadmap.id}>
                <h3 className="text-xl font-bold mb-2">{roadmap.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {roadmap.description}
                </p>
                <div className="space-y-2">
                  {roadmap.milestones?.slice(0, 3).map((milestone) => (
                    <div key={milestone.id} className="flex items-center gap-2">
                      {milestone.completed ? (
                        <CheckCircle size={16} className="text-green-600" />
                      ) : (
                        <Circle size={16} className="text-gray-400" />
                      )}
                      <span className="text-sm">{milestone.title}</span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="text-center py-20">
            <h3 className="text-xl font-semibold mb-2">No roadmaps yet</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Create your first learning roadmap
            </p>
            <Button>Create Roadmap</Button>
          </Card>
        )}
      </div>
    </div>
  );
};

export default RoadmapPage;