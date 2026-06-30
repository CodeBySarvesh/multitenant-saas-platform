from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace", "created_at", "updated_at")
    search_fields = ("name", "workspace__name")
    list_filter = ("workspace", "created_at")
    ordering = ("-created_at",)