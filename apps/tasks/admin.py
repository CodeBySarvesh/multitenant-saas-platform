from django.contrib import admin
from apps.tasks.models import Task


@admin.register(Task)
class taskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "status","project", "assigned_to")