from django.urls import path, re_path
from pulse_tracer import views

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'), 
    path('data_summary/', views.DataSummaryView.as_view(), name='data_summary'),
    path('health_care_provider/', views.HealthCareProviderDetailView.as_view(), name='health_care_provider'),
    path('health_care_provider_update/', views.HealthCareProviderUpdateView.as_view(), name='health_care_provider_update'),
    path('patient_list/', views.PatientListView.as_view(), name='patient_list'),
    path('patient/', views.PatientDetailView.as_view(), name='patient'),
    path('patient_update/', views.PatientUpdateView.as_view(), name='patient_update')
]