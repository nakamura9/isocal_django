from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DeleteView,
    DetailView)
from django.urls import reverse_lazy as reverse
from django_filters.views import FilterView
import os 
from calibration import forms, models, filters

class ContextMixin(object):
    context = {

    }
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.context)
        return context

CREATE_TEMPLATE = os.path.join('calibration', 'create_template.html')
DELETE_TEMPLATE = os.path.join('calibration', 'delete_template.html')

class DashboardView(TemplateView):
    template_name = os.path.join('calibration', 'dashboard.html')

class CustomerCreateView(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.CustomerForm
    context = {
        'title': 'Create New Customer'
    }

class CustomerUpdateView(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.CustomerForm
    context = {
        'title': 'Edit Customer'
    }

class CustomerListView(ContextMixin, FilterView):
    filterset_class = filters.CustomerFilter
    template_name = os.path.join('calibration', 'customer', 'list.html')
    queryset = models.Customer.objects.all()
    context = {
        'title': 'Customer List',
        'new_link': reverse('calibration:create-customer')
    }
    

class CustomerDetailView(DetailView):
    template_name = os.path.join('calibration', 'customer', 'details.html')
    model = models.Customer

class CustomerDeleteView(DeleteView):
    template_name = DELETE_TEMPLATE
    success_url = reverse('calibration:customer-list')
    model = models.Customer


class StandardCreateView(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.StandardForm
    context = {
        'title': 'Create Standard'
    }

class StandardUpdateView(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.StandardForm
    context = {
        'title': 'Edit Standard'
    }

class StandardListView(ContextMixin, FilterView):
    template_name = os.path.join('calibration','standard', 'list.html')
    queryset = models.Standard.objects.all()
    filterset_class = filters.StandardFilter
    context = {
        'title': 'Standards List',
        'new_link': reverse('calibration:create-standard')
    }

class StandardDetailView(DetailView):
    template_name = os.path.join('calibration', 'standard', 'details.html')
    model = models.Standard

class StandardDeleteView(DeleteView):
    template_name = DELETE_TEMPLATE
    success_url = reverse('calibration:standard-list')
    model = models.Standard


class CalibrationListView(ContextMixin, FilterView):
    template_name = os.path.join('calibration', 'list.html')
    queryset = models.GenericCalibration.objects.all()
    filterset_class = filters.CalibrationFilter
    context = {
        'title': 'Calibrations List',
    }