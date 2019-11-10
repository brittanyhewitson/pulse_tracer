import datetime
from django.utils import timezone

from pulse_tracer.models import (
    HeartRate,
    RespiratoryRate,
    ROI,
    Patient,
    HealthCare,
)

def get_weekly_summary(patient):

    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)

    # TODO: Change this to actually query the database 
    labels = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"]
    hr_data = [1, 24, 3, 54, 5, 16, 7]
    rr_data = [8, 22, 30, 41, 12, 13, 14]
    return labels, hr_data, rr_data

    