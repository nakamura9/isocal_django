from django.db import models
from django.shortcuts import reverse
import datetime
from statistics import mean, stdev
from builtins import round
import math

class Profile(models.Model):
    user = models.OneToOneField('auth.user', on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=16, choices=[
        ('technician', 'Technician'),
        ('admin', 'Admin')
        ])

    def __str__(self):
        return self.user.username

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
        total += self.genericcalibration_set.filter(certificate_number__isnull=True).count()
        total+= self.autoclave_set.filter(certificate_number__isnull=True).count()
        total += self.balance_set.filter(certificate_number__isnull=True).count()
        return total 


    @property
    def total(self):
        total = 0
        total += self.genericcalibration_set.all().count()
        total+= self.autoclave_set.all().count()
        total += self.balance_set.all().count()
        return total 

    @property
    def completed(self):
        return self.total - self.outstanding


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
    certificate_number = models.CharField(blank=True, max_length=255, default='')
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
            if not self.due or self.due > datetime.date.today():
                return 'Pending Datasheet'
            return 'Overdue Datasheet'
            
        return 'Certificate'

    @property
    def uncertainty(self):
        raise NotImplementedError()

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

    @property
    def type_string(self):
        return 'autoclave'

    @property
    def uncertainty(self):
        '''all uncertainty calculations are performed in this method
        will calculate the uncertainty based on the recorded data
        it is the sum of the square of the resolution and the sum of the 
        squares of the individual measurement errors. In the case of an autoclave there are two'''
        return None

    @property
    def uncertainty_pressure(self):
        return math.sqrt(math.pow(self.resolution, 2) + \
            sum(math.pow(i.correction,2) for i in self.autoclavepressurecalibrationline_set.all()))
        

    @property
    def uncertainty_temp(self):
        return math.sqrt(math.pow(self.resolution_temp, 2) + \
            sum(math.pow(i.correction,2) for i in self.autoclavetemperaturecalibrationline_set.all()))

class AutoclaveTemperatureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.Autoclave', on_delete=models.CASCADE)
    input_signal = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)

    @property 
    def correction(self):
        return abs(self.input_signal - self.measured)


class AutoclavePressureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.Autoclave', on_delete=models.CASCADE)
    applied_mass = models.FloatField(default=0.0)
    input_pressure = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)

    @property
    def calculated_pressure(self):
        '''Ensure input mass is grams'''

        def calculate_pressure_psi(weight):
            return (weight/45.19)+5.0150254481

        def calculate_pressure_bar(weight):
            return calculate_pressure_psi(weight) / 14.4038
                
        def calculate_pressure_kpa(weight):
            return calculate_pressure_bar(weight) * 100
            
        def calculate_pressure_mpa(weight):
            return calculate_pressure_bar(weight) / 10
            
        def calculate_pressure_pa(weight):
            return calculate_pressure_bar(weight) / 100000


        units = {
            'bar': calculate_pressure_bar,
            'kpa': calculate_pressure_kpa,
            'mpa': calculate_pressure_mpa,
            'pa': calculate_pressure_pa,
            'psi': calculate_pressure_psi,
        }
        calculator  = units.get(self.calibration.units)
        if not calculator:
            return 0

        return calculator(self.applied_mass)


    @property
    def correction(self):
        return abs(self.measured - self.calculated_pressure)


class GenericCalibration(Calibration):
    type = models.CharField(max_length=16)

    @property
    def type_string(self):
        return self.type

    @property 
    def uncertainty(self):
        '''all uncertainty calculations are performed in this method
        will calculate the uncertainty based on the recorded data
        it is the sum of the square of the resolution and the sum of the 
        squares of the individual measurement errors. In the case of an autoclave there are two'''
        return math.sqrt(math.pow(self.resolution, 2) + \
            sum(math.pow(i.correction,2) for i in self.genericcalibrationline_set.all()))


class GenericCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.GenericCalibration', on_delete=models.CASCADE)
    input_signal = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)

    @property 
    def correction(self):
        return abs(self.input_signal - self.measured)


class PressureCalibrationLine(models.Model):
    calibration = models.ForeignKey('calibration.GenericCalibration', on_delete=models.CASCADE)
    applied_mass = models.FloatField(default=0.0)
    input_pressure = models.FloatField(default=0.0)
    measured = models.FloatField(default=0.0)

    @property
    def calculated_pressure(self):
        '''Ensure input mass is grams'''

        def calculate_pressure_psi(weight):
            return (weight/45.19)+5.0150254481

        def calculate_pressure_bar(weight):
            return calculate_pressure_psi(weight) / 14.4038
                
        def calculate_pressure_kpa(weight):
            return calculate_pressure_bar(weight) * 100
            
        def calculate_pressure_mpa(weight):
            return calculate_pressure_bar(weight) / 10
            
        def calculate_pressure_pa(weight):
            return calculate_pressure_bar(weight) / 100000


        units = {
            'bar': calculate_pressure_bar,
            'kpa': calculate_pressure_kpa,
            'mpa': calculate_pressure_mpa,
            'pa': calculate_pressure_pa,
            'psi': calculate_pressure_psi,
        }
        print(self.calibration.units)
        calculator  = units.get(self.calibration.units)
        if not calculator:
            return 0

        return calculator(self.applied_mass)


    @property
    def correction(self):
        pass

class Balance(Calibration):
    @property
    def cold_nominal(self):
        qs = self.balancecoldstart_set.all()
        if qs.exists():
            return qs.first().nominal

    @property 
    def cold_drift(self):
        '''the total cold start readings
        average of maximum and minimum values
        test_weight value - ((max + min)/2) '''
        cold_values = [i.measurement for i in self.balancecoldstart_set.all()]
        if len(cold_values) > 0:
            average_over_span = (min(cold_values) + max(cold_values)) / 2
            return round(abs(float(self.balancecoldstart_set.first().nominal) - average_over_span), 4) #TODO change


    @property
    def type_string(self):
        return 'balance'

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

    @property 
    def half_repeat(self):
        readings = [i.half_load for i in self.balancerepeatability_set.all()]
        if len(readings) == 0:
            return 0
        return stdev(readings)

    @property
    def full_repeat(self):
        readings = [i.full_load for i in self.balancerepeatability_set.all()]
        if len(readings) == 0:
            return 0
        return stdev(readings)

    @property
    def uncertainty(self):
        """overall uncertainty of the data derived from the 
        uncertainty of the standards, the measurements
        drift, repeatbility """

        def squareroot_of_sum_of_squares(l):
            squares = [math.pow(i, 2) for i in l]
            return math.sqrt(sum(squares))

        std_uncertainty = squareroot_of_sum_of_squares([i.uncertainty for i in \
                                self.standard.standardline_set.all()])
        
        resolution_uncertainty = (self.resolution / 2) / math.sqrt(3)
        drift_uncertainty = self.cold_drift / math.sqrt(3)
        repeatability_uncertainty = squareroot_of_sum_of_squares(
            [self.half_repeat, self.full_repeat])
        
        return round(squareroot_of_sum_of_squares([std_uncertainty,
                    resolution_uncertainty,
                    drift_uncertainty,
                    repeatability_uncertainty]) * 2, 4)

    @property
    def up_down_linearity(self):
        readings = [mea for mea in self.balancelinearityupdown_set.all()]
        print(readings)
        up = readings[:5]
        
        down = readings[4:9]
        up2 = readings[10:15]
        
        print(len(up))
        print(len(up2))
        print(len(down))

        if len(up) != len(down) or len(up) != len(up2):
            return None

        res = []
        for i in range(5):
            data = {}
            data['nom'] = up[i].nominal
            data['actual'] = up[i].actual
            data['up'] = up[i].measurement
            data['down'] = down[i].measurement
            data['up2'] = up2[i].measurement
            reading_list =[up[i].measurement, 
                                down[i].measurement, 
                                up2[i].measurement]
            data['avg'] = round(mean(reading_list), 4)
            data['stdev'] = round(stdev(reading_list), 4)
            data['diff'] = round(abs(up[i].actual - mean(reading_list)),4)
            
            res.append(data)

        return res

    @property
    def repeat_half_average(self):
        return mean([i.half_load for i in self.balancerepeatability_set.all()])

    @property
    def repeat_full_average(self):
        return mean([i.full_load for i in self.balancerepeatability_set.all()])
        

    @property
    def repeat_half_stdev(self):
        if self.balancerepeatability_set.all().count() > 1:
            return round(stdev([i.half_load for i in self.balancerepeatability_set.all()]), 4)
        

    @property
    def repeat_full_stdev(self):
        if self.balancerepeatability_set.all().count() > 1:
            return round(stdev([i.full_load for i in self.balancerepeatability_set.all()]), 4)

    @property 
    def off_center_min(self):
        return min(i.measurement for i in self.balanceoffcenter_set.all())

    @property 
    def off_center_max(self):
        return max(i.measurement for i in self.balanceoffcenter_set.all())

    @property 
    def off_center_mean(self):
        return mean(i.measurement for i in self.balanceoffcenter_set.all())

    @property 
    def off_center_min_error(self):
        return min(i.difference for i in self.balanceoffcenter_set.all())

    @property 
    def off_center_stdev(self):
        return stdev(i.measurement for i in self.balanceoffcenter_set.all())

class BalanceColdStart(models.Model):
    #up to 5 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)
    nominal = models.FloatField(default=0.0)

    @property
    def actual(self):
        return 0#TODO fix

    @property
    def difference(self):
        return abs(self.nominal - self.measurement)


class BalanceSettlingTime(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)


class BalanceLinearityUpDown(models.Model):
    #up to 15 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)

    @property 
    def closest(self):
        std = self.calibration.standard
        if not std:
            return 

        closest_id = None
        smallest_difference = None
        for line in std.standardline_set.all():
            diff = abs(self.measurement - line.actual)
            if not smallest_difference or diff < smallest_difference:
                closest_id = line.id

        return StandardLine.objects.get(pk=closest_id)

    @property
    def nominal(self):
        if self.closest:
            return self.closest.nominal

    @property 
    def actual(self):
        if self.closest:
            return self.closest.actual

class BalanceLinearity(models.Model):
    #up to 5 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    actual = models.FloatField(default=0.0)
    nominal = models.FloatField(default=0.0)
    measurement = models.FloatField(default=0.0)

    @property
    def difference(self):
        return abs(self.measurement - self.actual)

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


    @property 
    def closest_half(self):
        std = self.calibration.standard
        if not std:
            return 

        closest_id = None
        smallest_difference = None
        for line in std.standardline_set.all():
            diff = abs(self.half_load - line.actual)
            if not smallest_difference or diff < smallest_difference:
                closest_id = line.id

        return StandardLine.objects.get(pk=closest_id)

    @property 
    def closest_full(self):
        std = self.calibration.standard
        if not std:
            return 

        closest_id = None
        smallest_difference = None
        for line in std.standardline_set.all():
            diff = abs(self.full_load - line.actual)
            if not smallest_difference or diff < smallest_difference:
                closest_id = line.id

        return StandardLine.objects.get(pk=closest_id)

    @property
    def nominal_half(self):
        if self.closest_half:
            return self.closest_half.nominal

    @property
    def nominal_full(self):
        if self.closest_full:
            return self.closest_full.nominal

    @property 
    def actual_half(self):
        if self.closest_half:
            return self.closest_half.actual

    @property 
    def actual_full(self):
        if self.closest_full:
            return self.closest_full.actual

class BalanceOffCenter(models.Model):
    #up to 10 measurements
    calibration = models.ForeignKey('calibration.Balance', on_delete=models.CASCADE)
    measurement = models.FloatField(default=0.0)
    mass_piece = models.FloatField(default=0.0)

    @property 
    def difference(self):
        return abs(self.mass_piece - self. measurement)