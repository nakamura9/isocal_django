from django.db import models
from django.shortcuts import reverse
import datetime

class Profile(models.Model):
    user = models.OneToOneField('auth.user', on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=16, choices=[
        ('technician', 'Technician'),
        ('admin', 'Admin')
        ])

class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True) 
    email = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    
    def get_absolute_url(self):
        return reverse("calibration:customer-details", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.name


class Calibration(models.Model):
    class Meta:
        abstract = True

    cerficate_timestamp = models.DateTimeField(null=True)
    date = models.DateField()
    start_time = models.TimeField(),
    customer = models.ForeignKey('calibration.customer', 
        on_delete=models.SET_NULL, null=True)
    due = models.DateField()
    serial = models.CharField(max_length=255, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    immersion_depth = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    name_of_instrument = models.CharField(max_length=255, blank=True)
    resolution = models.FloatField()
    units = models.CharField(max_length=255, blank=True)
    standard = models.ForeignKey('calibration.standard', 
        on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=255, blank=True)
    range_lower = models.FloatField(default=0.0)
    range_upper = models.FloatField(default=0.0)
    comments = models.TextField()

    @property
    def status(self):
        if not self.cerficate_timestamp:
            if self.due > datetime.date.today():
                return 'Pending Datasheet'
            return 'Overdue Datasheet'
            
        return 'Certificate'

class Standard(models.Model):
    name = models.CharField(max_length=255, unique=True)
    certificate = models.CharField(max_length=255)
    serial = models.CharField(max_length=255)
    traceability = models.TextField()

    def get_absolute_url(self):
        return reverse("calibration:standard-details", kwargs={"pk": self.pk})
    

class StandardLine(models.Model):
    standard = models.ForeignKey('calibration.standard', 
        on_delete=models.CASCADE)
    nominal = models.FloatField()
    actual = models.FloatField()
    uncertainty = models.FloatField()

class Autoclave(Calibration):
    #defaults are pressure
    range_temp_lower = models.FloatField()
    range_temp_upper = models.FloatField()
    resolution_temp = models.FloatField()
    temp_standard = models.ForeignKey('calibration.standard', 
        on_delete=models.CASCADE, related_name='temperature')
    temp_unit = models.CharField(max_length=255)

class GenericCalibration(Calibration):
    type = models.CharField(max_length=16)


class Balance(Calibration):
    pass