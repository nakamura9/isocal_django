from django.contrib import admin
from calibration import models 

# Register your models here.
admin.site.register(models.Profile)
admin.site.register(models.Customer)
admin.site.register(models.Standard)
admin.site.register(models.StandardLine)
admin.site.register(models.Autoclave)
admin.site.register(models.AutoclaveTemperatureCalibrationLine)
admin.site.register(models.AutoclavePressureCalibrationLine)
admin.site.register(models.GenericCalibration)
admin.site.register(models.GenericCalibrationLine)
admin.site.register(models.PressureCalibrationLine)
admin.site.register(models.Balance)
admin.site.register(models.BalanceColdStart)
admin.site.register(models.BalanceSettlingTime)
admin.site.register(models.BalanceLinearity)
admin.site.register(models.BalanceLinearityUpDown)
admin.site.register(models.BalanceRepeatability)
admin.site.register(models.BalanceTaringLinearity)
admin.site.register(models.BalanceOffCenter)









