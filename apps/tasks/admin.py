from django.contrib import admin
from apps.tasks.models import Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Task._meta.fields] + ["deleted"]

    def get_queryset(self, request):
        return Task.all_objects.all()

    @admin.display(boolean=True, description="Deleted")
    def deleted(self, obj):
        return obj.is_deleted
    
@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TaskComment._meta.fields] + ["is_deleted"]

    def get_queryset(self, request):
        return TaskComment.all_objects.all()

    @admin.display(boolean=True, description="Deleted")
    def is_deleted(self, obj):
        return obj.is_deleted