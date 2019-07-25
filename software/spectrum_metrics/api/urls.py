from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers, permissions
from . import views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sprectrum Metrics API",
        default_version='v1',),
   validators=['ssv'],
   public=True,
   permission_classes=(permissions.IsAuthenticatedOrReadOnly,),
)


router = routers.DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'rois', views.ROIViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'health_care_providers', views.HealthCareViewSet)
router.register(r'heart_rates', views.HeartRateViewSet)
router.register(r'respiratory_rates', views.RespiratoryRateViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
]