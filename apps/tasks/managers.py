from apps.common.managers import AllObjectsManager, SoftDeleteManager, SoftDeleteQuerySet


class TaskQuerySet(SoftDeleteQuerySet):

    def for_workspace(self, workspace):

        if workspace is None:
            return self.none()

        return self.filter(
            project__workspace=workspace
        )
    
class TaskManager(SoftDeleteManager):

    def get_queryset(self):
        return TaskQuerySet(
            self.model,
            using=self._db
        ).active()

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    

class AllTaskManager(AllObjectsManager):

    def get_queryset(self):
        return TaskQuerySet(
            self.model,
            using=self._db
        )

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    
# ----- for task Comment------
class TaskCommentQuerySet(SoftDeleteQuerySet):

    def for_workspace(self, workspace):

        if workspace is None:
            return self.none()

        return self.filter(
           task__project__workspace=workspace
        )
    
class TaskCommentManager(SoftDeleteManager):

    def get_queryset(self):
        return TaskCommentQuerySet(
            self.model,
            using=self._db
        ).active()

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    

class AllTaskCommentManager(AllObjectsManager):

    def get_queryset(self):
        return TaskCommentQuerySet(
            self.model,
            using=self._db
        )

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    
# ----- for task Attactment------
class TaskAttachmentQuerySet(SoftDeleteQuerySet):

    def for_workspace(self, workspace):

        if workspace is None:
            return self.none()

        return self.filter(
           task__project__workspace=workspace
        )
    
class TaskAttachmentManager(SoftDeleteManager):

    def get_queryset(self):
        return TaskAttachmentQuerySet(
            self.model,
            using=self._db
        ).active()

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)
    

class AllTaskAttachmentManager(AllObjectsManager):

    def get_queryset(self):
        return TaskAttachmentQuerySet(
            self.model,
            using=self._db
        )

    def for_workspace(self, workspace):
        return self.get_queryset().for_workspace(workspace)