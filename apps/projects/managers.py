from apps.common.managers import AllObjectsManager, SoftDeleteManager, SoftDeleteQuerySet


class ProjectQuerySet(SoftDeleteQuerySet):

    def for_workspace(self, workspace):
        if workspace is None:
            return self.none()

        return self.filter(
            workspace=workspace
        )
    
class ProjectManager(SoftDeleteManager):

    def get_queryset(self):
        return ProjectQuerySet(
            self.model,
            using=self._db
        ).active()

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    

class AllProjectManager(AllObjectsManager):

    def get_queryset(self):
        return ProjectQuerySet(
            self.model,
            using=self._db
        )

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)