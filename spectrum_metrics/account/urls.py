from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	path('', auth_views.LoginView.as_view(), name='login'), 
	path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    re_path(r'create_device/(?P<pk>\d+)/$', views.CreateDeviceView.as_view(), name='create_device'),
    re_path(r'create_patient/(?P<pk>\d+)/(?P<device_id>\d+)$', views.CreatePatientView.as_view(), name='create_patient'),
    re_path(r'create_health_care/(?P<pk>\d+)/$', views.CreateHealthCareView.as_view(), name='create_health_care'),
]