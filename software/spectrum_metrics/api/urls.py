from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'rois', views.ROIViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'helath_care_providers', views.HealthCareViewSet)
router.register(r'heart_rates', views.HeartRateViewSet)
router.register(r'respiratory_rates', views.RespiratoryRateViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]