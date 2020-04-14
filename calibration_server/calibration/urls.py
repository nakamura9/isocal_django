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
    path('balance-calibration-list/', views.BalanceCalibrationListView.as_view(), 
        name='balance-calibration-list'),
    path('balance-calibration-detail/<int:pk>/', views.BalanceDetailView.as_view(), 
        name='balance-calibration-detail'),
    path('autoclave-calibration-list/', views.AutoclaveCalibrationListView.as_view(), 
        name='autoclave-calibration-list'),
    path('upload/', views.UploadView.as_view(), 
        name='upload'),
    path('upload-standards/', views.upload_standards, 
        name='upload-standards'),
    path('upload-calibrations/', views.upload_calibrations, 
        name='upload-calibrations'),
]
