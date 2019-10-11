from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'), 
	path('data_summary/', views.DataSummaryView.as_view(), name='data_summary'),
	path('health_care_provider/', views.HealthCareProviderDetailView.as_view(), name='health_care_provider'),
	path('patient_list/', views.PatientListView.as_view(), name='patient_list')
]