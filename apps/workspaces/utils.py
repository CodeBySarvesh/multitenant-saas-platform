from .models import Membership

def get_user_membership(user, workspace):
    return Membership.objects.filter(
        user=user,
        workspace=workspace
    ).first()