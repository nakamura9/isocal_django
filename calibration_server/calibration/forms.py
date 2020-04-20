from django import forms 
from calibration import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Div, Row, Column, Submit)
from django.contrib.auth import authenticate

class CustomerForm(forms.ModelForm):
    class Meta:
        fields ="__all__"
        model = models.Customer
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 8
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', 'phone', 'email', css_class='col-6'),
                Column('address', css_class='col-6')
                )
        )
        self.helper.add_input(Submit('submit', 'Submit'))



class StandardForm(forms.ModelForm):
    class Meta:
        fields ="__all__"
        model = models.Standard
        widgets = {
            'traceability': forms.Textarea(attrs={
                'rows': 6
            })
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'certificate',
            'serial',
            'traceability'
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class CertificateForm(forms.Form):
    temperature = forms.CharField(widget=forms.NumberInput)
    humidity = forms.CharField(widget=forms.NumberInput)
    technician = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'temperature',
            'humidity',
            'technician'
            
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class ProfileCreateForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget =forms.PasswordInput)
    confirm_password  = forms.CharField(widget =forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    profile_type = forms.ChoiceField(choices=[('technician', 'Technician'), ('admin', 'Admin')])
    authorization_code = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data['authorization_code'] != "17025":
            raise forms.ValidationError('The authorization code is incorrect.')

        if len(data['password']) < 8:
            raise forms.ValidationError('The password is too short')
        if data['password'] != data['confirm_password']:
            raise forms.ValidationError('The passwords supplied do not match')

        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name', css_class='col-6'), Column('last_name', css_class='col-6')),
            Row(Column('password', css_class='col-6'), Column('confirm_password', css_class='col-6')),
            Row(Column('username', css_class='col-6'), Column('profile_type', css_class='col-6')),
            'authorization_code'            
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ProfilePasswordChangeForm(forms.Form):
    profile = forms.ModelChoiceField(models.Profile.objects.all())
    old_password = forms.CharField(widget =forms.PasswordInput)
    new_password = forms.CharField(widget =forms.PasswordInput)
    confirm_new_password  = forms.CharField(widget =forms.PasswordInput)
    
    def clean(self):
        data = super().clean()
       
        if not authenticate(username=data['profile'].user.username, password=data['old_password']):
            raise forms.ValidationError('The password supplied is incorrect')

        if len(data['new_password']) < 8:
            raise forms.ValidationError('The password is too short')
        if data['new_password'] != data['confirm_new_password']:
            raise forms.ValidationError('The passwords supplied do not match')

        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
           'profile',
           'old_password',
           'new_password',
           'confirm_new_password'         
        )
        self.helper.add_input(Submit('submit', 'Submit'))

class ProfilePasswordResetForm(forms.Form):
    profile = forms.ModelChoiceField(models.Profile.objects.all())
    authorization_code = forms.CharField(widget =forms.PasswordInput)
    new_password = forms.CharField(widget =forms.PasswordInput)
    confirm_new_password  = forms.CharField(widget =forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
           'profile',
           'new_password',
           'confirm_new_password',
            'authorization_code'            
        )
        self.helper.add_input(Submit('submit', 'Submit'))


    def clean(self):
        data = super().clean()
        if data['authorization_code'] != "17025":
            raise forms.ValidationError('The authorization code is incorrect.')
        
        if len(data['new_password']) < 8:
            raise forms.ValidationError('The password is too short')
        if data['new_password'] != data['confirm_new_password']:
            raise forms.ValidationError('The passwords supplied do not match')

        return data