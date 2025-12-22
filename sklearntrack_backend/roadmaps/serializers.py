# FILE: roadmaps/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import Roadmap, Milestone, RoadmapTask


class RoadmapTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadmapTask
        fields = [
            'id', 'title', 'description', 'priority', 'completed',
            'course', 'topic', 'note', 'due_date', 'completed_at'
        ]


class MilestoneSerializer(serializers.ModelSerializer):
    tasks = RoadmapTaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Milestone
        fields = [
            'id', 'title', 'description', 'order', 'completed',
            'due_date', 'completed_at', 'tasks'
        ]


class RoadmapSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Roadmap
        fields = [
            'id', 'title', 'description', 'target_completion_date',
            'milestones', 'created_at', 'updated_at'
        ]

