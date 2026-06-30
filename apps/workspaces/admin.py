from django.contrib import admin
from .models import Workspace, Membership


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    list_filter = ("created_at",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "workspace", "role")
    list_filter = ("role", "workspace")
    search_fields = (
        "user__username",
        "user__email",
        "workspace__name",
    )