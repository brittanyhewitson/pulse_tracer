from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'), 
	path('data_summary/', views.DataSummaryView.as_view(), name='data_summary'),
]