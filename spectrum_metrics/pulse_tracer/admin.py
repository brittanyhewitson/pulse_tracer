from django.contrib import admin

from .models import(
    Device, 
    ROI, 
    Patient, 
    HealthCare,
    HeartRate,
    RespiratoryRate,
    User,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Device)
admin.site.register(ROI)
admin.site.register(Patient)
admin.site.register(HealthCare)
admin.site.register(HeartRate)
admin.site.register(RespiratoryRate)