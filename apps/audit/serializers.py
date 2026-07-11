from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    action_display = serializers.CharField(
        source="get_action_display",
        read_only=True
    )

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user_email",
            "action",
            "action_display",
            "message",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user_email",
            "action_display",
            "created_at",
        ]