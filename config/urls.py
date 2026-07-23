from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.workspaces.urls')),
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.projects.urls')),
    path('api/v1/', include('apps.audit.urls')),

     # OpenAPI schema
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # ReDoc
    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
