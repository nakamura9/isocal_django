from django import forms 
from calibration import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Div, Row, Column, Submit)


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