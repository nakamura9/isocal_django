import django_filters
from calibration import models


class CalibrationFilter(django_filters.FilterSet):
    class Meta:
        fields = {
            'type': ['exact'],
            'date': ['exact', 'gt', 'lt'],
            'customer': ['exact']
        }
        model = models.GenericCalibration


class CustomerFilter(django_filters.FilterSet):
    class Meta:
        fields = {
            'name': ['icontains']
        }
        model = models.Customer


class StandardFilter(django_filters.FilterSet):
    class Meta:
        fields = {
            'name': ['icontains'],
            'serial': ['icontains']
        }
        model = models.Standard