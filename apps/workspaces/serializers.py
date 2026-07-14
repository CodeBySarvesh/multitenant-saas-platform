from rest_framework import serializers

from apps.workspaces.models import Membership, Workspace

class WorkspaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workspace
        fields = [
            "id","name","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]


class MembershipSerializer(serializers.ModelSerializer):

    workspace = WorkspaceSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = [
            "workspace",
            "role",
            "created_at",
        ]