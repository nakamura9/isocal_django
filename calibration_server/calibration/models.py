from django.db import models
from django.shortcuts import reverse
import datetime
from statistics import mean

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

    @property
    def outstanding(self):
        total = 0
        total += self.genericcalibration_set.filter(certificate_timestamp__isnull=True).count()
        total+= self.autoclave_set.filter(certificate_timestamp__isnull=True).count()
        total += self.balance_set.filter(certificate_timestamp__isnull=True).count()
        return total 


    @property
    def completed(self):
        total = 0
        total += self.genericcalibration_set.filter(certificate_timestamp__isnull=False).count()
        total+= self.autoclave_set.filter(certificate_timestamp__isnull=False).count()
        total += self.balance_set.filter(certificate_timestamp__isnull=False).count()
        return total 


    @property
    def latest(self):
        calibrations = []
        if self.genericcalibration_set.all().count() > 0:
            calibrations.append(self.genericcalibration_set.latest('date').date)

        if self.autoclave_set.all().count() > 0:
            calibrations.append(self.autoclave_set.latest('date').date)

        if self.balance_set.all().count() > 0:
            calibrations.append(self.balance_set.latest('date').date)
        
        if len(calibrations) == 0:
            return None

        return max(calibrations)
    
    def __str__(self):
        return self.name


class Calibration(models.Model):
    class Meta:
        abstract = True

    certificate_timestamp = models.DateTimeField(null=True)
    date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    temperature = models.CharField(blank=True, default="", max_length=255)
    humidity = models.CharField(blank=True, default='', max_length=255)
    customer = models.ForeignKey('calibration.customer', 
        on_delete=models.SET_NULL, null=True)
    due = models.DateField(blank=True,null=True)
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
    comments = models.TextField(blank=True)

    @property
    def status(self):
        if not self.certificate_timestamp:
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


class AutoclaveTemperatureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.Autoclave', on_delete=models.CASCADE)
    input_signal = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)


class AutoclavePressureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.Autoclave', on_delete=models.CASCADE)
    applied_mass = models.FloatField(default=0.0)
    input_pressure = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)


class GenericCalibration(Calibration):
    type = models.CharField(max_length=16)

class GenericCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.GenericCalibration', on_delete=models.CASCADE)
    input_signal = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)


class PressureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.GenericCalibration', on_delete=models.CASCADE)
    applied_mass = models.FloatField(default=0.0)
    input_pressure = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)


class Balance(Calibration):

    @property 
    def standard_obj(self):
        return Standard.objects.get(name=self.standard)
        
    @property
    def corner_weight(self):
        qs = self.balanceoffcenter_set.all()
        if qs.exists():
            return qs.first().mass_piece

        return None

    @property
    def max_corner_error(self):
        if self.corner_weight:
            max_error = 0 
            for i in self.balanceoffcenter_set.all():
                error = abs(i.measurement - self.corner_weight)
                if error > max_error:
                    max_error = error

            return max_error
        return None

    @property
    def settling_average(self):
        return mean(i.measurement for i in self.balancesettlingtime_set.all())

class BalanceColdStart(models.Model):
    #up to 5 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)
    nominal = models.FloatField(default=0.0)


class BalanceSettlingTime(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)


class BalanceLinearityUpDown(models.Model):
    #up to 15 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)

class BalanceLinearity(models.Model):
    #up to 5 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    actual = models.FloatField(default=0.0)
    nominal = models.FloatField(default=0.0)
    measurement = models.FloatField(default=0.0)

class BalanceTaringLinearity(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    tare = models.FloatField(default=0.0)
    indicated = models.FloatField(default=0.0)


class BalanceRepeatability(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    half_load = models.FloatField(default=0.0)
    full_load = models.FloatField(default=0.0)

class BalanceOffCenter(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)
    mass_piece = models.FloatField(default=0.0)