from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "user",
        "action",
        "message",
        "created_at",
    )

    list_filter = (
        "action",
        "workspace",
        "created_at",
    )

    search_fields = (
        "message",
        "user__email",
        "action",
    )

    readonly_fields = (
        "user",
        "workspace",
        "action",
        "message",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False