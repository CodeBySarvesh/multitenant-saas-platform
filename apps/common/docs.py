from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

WORKSPACE_HEADER = OpenApiParameter(
    name="X-Workspace-ID",
    location=OpenApiParameter.HEADER,
    type=OpenApiTypes.INT,
    required=True,
    description="Workspace ID",
)