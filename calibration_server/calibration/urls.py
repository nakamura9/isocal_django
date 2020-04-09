from calibration import views
from django.urls import path

appname = 'calibration'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('create-customer/', views.CustomerCreateView.as_view(), 
        name='create-customer'),
    path('customer-list/', views.CustomerListView.as_view(), 
        name='customer-list'),
    path('update-customer/<int:pk>', views.CustomerUpdateView.as_view(), 
        name='update-customer'),
    path('customer-details/<int:pk>', views.CustomerDetailView.as_view(), 
        name='customer-details'),
    path('create-standard/', views.StandardCreateView.as_view(), 
        name='create-standard'),
    path('standard-list/', views.StandardListView.as_view(), 
        name='standard-list'),
    path('update-standard/<int:pk>', views.StandardUpdateView.as_view(), 
        name='update-standard'),
    path('standard-details/<int:pk>', views.StandardDetailView.as_view(), 
        name='standard-details'),
    path('calibration-list/', views.CalibrationListView.as_view(), 
        name='calibration-list'),
    path('upload/', views.UploadView.as_view(), 
        name='upload'),
]
