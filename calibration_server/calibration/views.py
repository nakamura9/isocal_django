from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DeleteView,
    FormView,
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
from django.contrib.auth.models import User

from django_weasyprint import WeasyTemplateResponseMixin
from calibration_server import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


class ContextMixin(object):
    context = {

    }
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.context)
        return context

class ProfileCreateView(ContextMixin, FormView):
    template_name = os.path.join('calibration', 'create_template.html')
    form_class = forms.ProfileCreateForm
    context = {
        'title': 'Create Profile'
    }
    success_url = '/login/'

    def form_valid(self, form):
        resp = super().form_valid(form)
        usr = User.objects.create(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            )

        profile = models.Profile.objects.create(
            user=usr,
            profile_type=form.cleaned_data['profile_type']
        )
        return resp

class PasswordResetView(FormView):
    template_name = os.path.join('calibration', 'create_template.html')
    form_class = forms.ProfilePasswordResetForm
    context = {
        'title': 'Reset Profile Password'
    }
    success_url = '/login/'

    def form_valid(self, form):
        resp = super().form_valid(form)
        profile = form.cleaned_data['profile']
        profile.user.set_password(form.cleaned_data['new_password'])
        profile.user.save()
        profile.save()
        return resp

class PasswordChangeView(ContextMixin, FormView):
    template_name = os.path.join('calibration', 'create_template.html')
    form_class = forms.ProfilePasswordChangeForm
    context = {
        'title': 'Change Profile Password'
    }
    success_url = '/login/'

    def form_valid(self, form):
        resp = super().form_valid(form)
        profile = form.cleaned_data['profile']
        profile.user.set_password(form.cleaned_data['new_password'])
        profile.user.save()
        profile.save()
        return resp



CREATE_TEMPLATE = os.path.join('calibration', 'create_template.html')
DELETE_TEMPLATE = os.path.join('calibration', 'delete_template.html')

class DashboardView(TemplateView):
    template_name = os.path.join('calibration', 'dashboard.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = models.Customer.objects.all()
        context['standards'] = models.Standard.objects.all()
        outstanding_balances = models.Balance.objects.filter(certificate_number="").count()
        outstanding_autoclaves = models.Autoclave.objects.filter(certificate_number="").count()
        outstanding_generic = models.GenericCalibration.objects.filter(certificate_number="").count()
        context['outstanding'] = outstanding_autoclaves + outstanding_balances + outstanding_generic
        types = []
        types.append({'name': 'Balance', 'count': models.Balance.objects.all().count()})
        types.append({'name': 'Autoclave', 'count': models.Autoclave.objects.all().count()})
        types.append({
            'name': 'Temperature', 
            'count': models.GenericCalibration.objects.filter(type='temperature').count()
            })
        types.append({
            'name': 'Pressure', 
            'count': models.GenericCalibration.objects.filter(type='pressure').count()
            })
        types.append({
            'name': 'Current', 
            'count': models.GenericCalibration.objects.filter(type='current').count()
            })
        types.append({
            'name': 'Flow', 
            'count': models.GenericCalibration.objects.filter(type='flow').count()
            })
        types.append({
            'name': 'Voltage', 
            'count': models.GenericCalibration.objects.filter(type='voltage').count()
            })
        types.append({
            'name': 'PH', 
            'count': models.GenericCalibration.objects.filter(type='ph').count()
            })
        types.append({
            'name': 'Conductivity', 
            'count': models.GenericCalibration.objects.filter(type='conductivity').count()
            })
        context['types'] = types
        return context
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
    paginate_by = 10
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
    paginate_by = 10

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
    paginate_by = 10

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
    paginate_by = 10

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview'] = True
        return context

class BalancePDFView(WeasyTemplateResponseMixin, BalanceDetailView):
    pdf_filename = 'certificate.pdf'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview'] = False
        return context


class AutoclaveDetailView(DetailView):
    model = models.Autoclave
    template_name = os.path.join('calibration', 'certificates', 'autoclave.html')


class AutoclavePDFView(WeasyTemplateResponseMixin, AutoclaveDetailView):
    pdf_filename = 'certificate.pdf'

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

class GenericPDFView(WeasyTemplateResponseMixin, GenericDetailView):
    pdf_filename = 'certificate.pdf'

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

            
            half = cal.get('repeatability', [])[:5]
            full = cal.get('repeatability', [])[6:10]
            if len(half) == len(full):
                for i, j in zip(half, full):
                    models.BalanceRepeatability.objects.create(
                        calibration=bal,
                        half_load=i,
                        full_load=j
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

# def link_callback(uri, rel):
#     """
#     Convert HTML URIs to absolute system paths so xhtml2pdf can access those
#     resources.
#     This function is taken from an online source that provided xhtml2pdf.
#     """
#     # use short variable names
#     sUrl = settings.STATIC_URL # Typically /static/
#     sRoot = settings.STATIC_ROOT # Typically /home/userX/project_static/
#     mUrl = settings.MEDIA_URL # Typically /static/media/
#     mRoot = settings.MEDIA_ROOT # Typically /home/userX/project_static/media/
#     # convert URIs to absolute system paths
#     if uri.startswith(mUrl):
#         path = os.path.join(mRoot, uri.replace(mUrl, ""))
#     elif uri.startswith(sUrl):
#         path = os.path.join(sRoot, uri.replace(sUrl, ""))
#     else:
#         return uri
#     # make sure that file exists
#     if not os.path.isfile(path):
#         raise Exception(
#             'media URI must start with %s or %s' % (sUrl, mUrl)
#         )
#     return path

# def balance_pdf_generator(request, pk=None):
#     balance = models.Balance.objects.get(pk=pk)

#     # Create a Django response object, and specify content_type as pdf
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
#     template_path = os.path.join('calibration', 'certificates', 'balances.html')

#     template = get_template(template_path)
#     html = template.render({'object': balance})
    
#     # create a pdf
#     pisaStatus = pisa.CreatePDF(
#     html, dest=response, link_callback=link_callback)
    
#     # if error then show some view
#     if pisaStatus.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response


class GenerateCertificateView(FormView):
    form_class = forms.CertificateForm
    template_name = os.path.join('calibration', 'generate_certificate.html')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mapping = {
            'balance': '/balance-calibration-detail',
            'autoclave': '/autoclave-calibration-detail',
            'generic': '/calibration-detail',
        }
        context['frame_url'] =  f"{mapping[self.kwargs['type']]}/{self.kwargs['pk']}/"
        return context

    def form_valid(self, form):
        mapping = {
            'balance': models.Balance,
            'autoclave': models.Autoclave,
            'generic': models.GenericCalibration,
        }
        obj  = mapping.get(self.kwargs['type']).objects.get(pk=self.kwargs['pk'])
        obj.certificate_number = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{form.cleaned_data['technician']}"
        obj.temperature = form.cleaned_data['temperature']
        obj.humidity = form.cleaned_data['humidity']
        obj.save()

        return super().form_valid(form)

    def get_success_url(self):
        mapping = {
            'balance': reverse('calibration:balance-pdf', kwargs={'pk': self.kwargs['pk']}),
            'autoclave': reverse('calibration:autoclave-pdf', kwargs={'pk': self.kwargs['pk']}),
            'generic': reverse('calibration:generic-pdf', kwargs={'pk': self.kwargs['pk']}),
        }

        return mapping.get(self.kwargs['type'])
        