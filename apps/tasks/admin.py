from django.contrib import admin
from apps.tasks.models import Task, TaskAttachment, TaskComment


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
    

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "file",
        "uploaded_by",
        "is_deleted",
    )

    search_fields = (
        "task__id",
        "uploaded_by__username",
    )

    readonly_fields = (
        "uploaded_by",
    )