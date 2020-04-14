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
import socket 
from django.http import JsonResponse
import json
import datetime
from django.views.decorators.csrf import csrf_exempt


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
    model = models.Customer
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
    model = models.Standard
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


class AutoclaveCalibrationListView(ContextMixin, FilterView):
    template_name = os.path.join('calibration', 'autoclave_list.html')
    queryset = models.Autoclave.objects.all()
    filterset_class = filters.AutoclaveCalibrationFilter
    context = {
        'title': 'Autoclave Calibration List',
    }

class BalanceCalibrationListView(ContextMixin, FilterView):
    template_name = os.path.join('calibration', 'balance_list.html')
    queryset = models.Balance.objects.all()
    filterset_class = filters.BalanceCalibrationFilter
    context = {
        'title': 'Balance Calibrations List',
    }


class UploadView(ContextMixin, TemplateView):
    template_name = os.path.join('calibration', 'upload.html')
    context = {
        'ip': socket.gethostbyname(socket.gethostname())
    }


class BalanceDetailView(DetailView):
    model = models.Balance
    template_name = os.path.join('calibration', 'certificates', 'balances.html')


class AutoclaveDetailView(DetailView):
    model = models.Autoclave
    template_name = os.path.join('calibration', 'certificates', 'autoclave.html')

class GenericDetailView(DetailView):
    model = models.GenericCalibration
    def get_template_names(self):
        mapping = {
            'current': 'current.html',
            'voltage': 'voltage.html',
            'ph': 'ph.html',
            'volume': 'volume.html',
            'conductivity': 'conductivity.html',
            'tds': 'tds.html',
            'flow': 'flow.html',
            'temperature': 'temperature.html',
            'pressure': 'pressure.html'
        }
        
        if not self.object:
            self.get_object()

        return [os.path.join('calibration', 'certificates', mapping[self.object.type])]

@csrf_exempt
def upload_standards(request):
    print(request.body)
    data = json.loads(request.body)
    for std in data['standards']:
        if models.Standard.objects.filter(name=std['name']).exists():
            continue
        standard = models.Standard.objects.create(
            name=std['name'],
            certificate=std['certificate'],
            serial=std['serial'],
            traceability=std['traceability']
        )

        for line in std['data']:
            models.StandardLine.objects.create(
                standard=standard,
                nominal=line['nominal'],
                actual=line['actual'],
                uncertainty=line['uncertainty']
            )
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def upload_calibrations(request):
    print(request.body)
    data = json.loads(request.body)
    for cal in data['calibrations']:
        date, start_time = cal['date'].split('T')
        time = datetime.datetime.strptime(start_time.split('.')[0], '%H:%M:%S')
        customer = None
        cus_qs = models.Customer.objects.filter(name=cal['customer'])
        if cus_qs.exists():
            customer = cus_qs.first()
        else:
            customer = models.Customer.objects.create(name=cal['customer'])
        if cal['type'] == 'balance':
            bal = models.Balance.objects.create(
                date=date,
                start_time=time,
                customer=customer,
                manufacturer=cal['manufacturer'],
                serial=cal['serial'],
                immersion_depth=cal['immersion'],
                model=cal['model'],
                name_of_instrument=cal['instrument'],
                resolution=cal['resolution'],
                range_lower=cal['rangeLower'],
                range_upper=cal['rangeUpper'],
                units = cal['unit'],
                standard=models.Standard.objects.filter(
                    name=cal['standard']).first(),
                location=cal['location'],
                comments=cal.get('comments', '')
            )

            for cs in cal['cold_start']:
                models.BalanceColdStart.objects.create(
                    calibration=bal,
                    measurement=cs[1],
                    nominal=cal['cold_start_nominal']
                )

            for st in cal['settling_time']:
                models.BalanceSettlingTime.objects.create(
                    calibration=bal,
                    measurement=st[1],   
                )

            for lin in cal['linearity_up']:
                nominal, actual, linearity = lin
                models.BalanceLinearity.objects.create(
                    calibration=bal,
                    actual=actual,
                    nominal=nominal,
                    measurement=linearity
                )

            for lin in cal['linearity']:
                models.BalanceLinearityUpDown.objects.create(
                    calibration=bal,
                    measurement=lin[0],
                )

            for tare in cal['tare']:
                t, indicated = tare
                models.BalanceTaringLinearity.objects.create(
                    calibration=bal,
                    tare=t,
                    indicated=indicated
                )

            for rep in cal.get('repeatability', []):
                half, full = rep
                models.Repeatability.objects.create(
                    calibration=bal,
                    half_load=half,
                    full_load=full
                )
            for oc in cal['off_center_data']:
                models.BalanceOffCenter.objects.create(
                    calibration=bal,
                    measurement=oc[1],
                    mass_piece=cal['off_center_mass_piece']
                )
           
            continue

        elif cal['type'] == 'autoclave':
            auto = models.Autoclave.objects.create(
                date=date,
                start_time=time,
                customer=customer,
                manufacturer=cal['manufacturer'],
                serial=cal['serial'],
                immersion_depth=cal['immersion'],
                model=cal['model'],
                name_of_instrument=cal['instrument'],
                resolution=cal['pressureResolution'],
                range_lower=cal['pressureRangeLower'],
                range_upper=cal['pressureRangeUpper'],
                units = cal['pressureUnit'],
                standard=models.Standard.objects.filter(
                    name=cal['pressureStandard']).first(),
                resolution_temp=cal['resolution'],
                range_temp_lower=cal['rangeLower'],
                range_temp_upper=cal['rangeUpper'],
                temp_unit = cal['unit'],
                temp_standard=models.Standard.objects.filter(
                    name=cal['standard']).first(),
                location=cal['location'],
                comments=cal.get('comments', '')
            )

            for temp in cal['tempData']:
                inp, measured = temp
                models.AutoclaveTemperatureCalibrationLine.objects.create(
                    calibration=auto,
                    input_signal=inp,
                    measured=measured
                )

            for pres in cal['data']:
                inp, measured = pres
                models.AutoclavePressureCalibrationLine.objects.create(
                    calibration=auto,
                    applied_mass=inp,
                    measured=measured
                )
            continue
                
        gc = models.GenericCalibration.objects.create(
            date=date,
                start_time=time,
                customer=customer,
                manufacturer=cal['manufacturer'],
                serial=cal['serial'],
                immersion_depth=cal['immersion'],
                model=cal['model'],
                name_of_instrument=cal['instrument'],
                resolution=cal['resolution'],
                range_lower=cal['rangeLower'],
                range_upper=cal['rangeUpper'],
                units = cal['unit'],
                standard=models.Standard.objects.filter(
                    name=cal['standard']).first(),
                location=cal['location'],
                comments=cal.get('comments', ''),
                type=cal['type']
        )
        if cal['type'] == 'pressure':
            for pres in cal['data']:
                inp, measured = pres
                models.PressureCalibrationLine.objects.create(
                    calibration=gc,
                    applied_mass=inp,
                    measured=measured
                )
            continue

        else:
            for mea in cal['data']:
                inp, measured = mea
                models.GenericCalibrationLine.objects.create(
                    calibration=gc,
                    input_signal=inp,
                    measured=measured
                )
    
    
    return JsonResponse({'status': 'ok'})