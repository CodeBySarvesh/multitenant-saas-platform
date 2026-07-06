from rest_framework import serializers

from apps.tasks.models import Task
from apps.workspaces.models import Membership
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'status', 'created_at']


    def validate_assigned_to(self, user):
        request = self.context.get("request")

        if not user:
            return user

        workspace = request.workspace

        is_member = Membership.objects.filter(
            workspace=workspace,
            user=user
        ).exists()

        if not is_member:
            raise serializers.ValidationError("User not in this workspace")

        return user