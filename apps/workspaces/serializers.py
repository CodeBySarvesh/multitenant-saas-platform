from rest_framework import serializers

from apps.workspaces.models import Membership, Workspace

class WorkspaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workspace
        fields = [
            "id","name","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]


class MembershipReadSerializer(serializers.ModelSerializer):

    workspace = WorkspaceSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = [
            "workspace",
            "role",
            "created_at",
        ]

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_email",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_role(self, value):
        valid_roles = ["admin", "member", "owner"]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role.")
        return value
