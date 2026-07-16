from django.core.cache import cache
from django.conf import settings

from .models import Membership


def get_user_membership(user, workspace):

    if not user.is_authenticated or workspace is None:
        return None

    cache_key = f"membership:{user.id}:{workspace.id}"

    membership = cache.get(cache_key)

    if membership is not None:
        print("MEMBERSHIP CACHE HIT",membership.role)
        return membership

    print("MEMBERSHIP CACHE MISS")

    membership = (
        Membership.objects
        .select_related("user", "workspace")
        .filter(
            user=user,
            workspace=workspace
        )
        .first()
    )

    if membership:
        cache.set(
            cache_key,
            membership,
            timeout=settings.MEMBERSHIP_CACHE_TIMEOUT
        )

    return membership