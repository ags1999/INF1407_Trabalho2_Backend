from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include('core.urls')),

    # Documentação / Swagger
    # - /api/schema/       -> arquivo OpenAPI (YAML)
    # - /api/docs/         -> interface Swagger UI
    # - /api/redoc/        -> interface ReDoc (alternativa)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
