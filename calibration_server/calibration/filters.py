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


class BalanceCalibrationFilter(django_filters.FilterSet):
    class Meta:
        fields = {
            'date': ['exact', 'gt', 'lt'],
            'customer': ['exact']
        }
        model = models.Balance



class AutoclaveCalibrationFilter(django_filters.FilterSet):
    class Meta:
        fields = {
            'date': ['exact', 'gt', 'lt'],
            'customer': ['exact']
        }
        model = models.Autoclave



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