from django.contrib import admin
from .models import Workspace, Membership


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_owners']

    def get_owners(self, obj):
        owners = Membership.objects.filter(
            workspace=obj,
            role='owner'
        ).select_related('user')

        return ", ".join([m.user.email for m in owners])

    get_owners.short_description = "Owners"


admin.site.register(Workspace, WorkspaceAdmin)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "workspace", "role")
    list_filter = ("role", "workspace")
    search_fields = (
        "user__username",
        "user__email",
        "workspace__name",
    )