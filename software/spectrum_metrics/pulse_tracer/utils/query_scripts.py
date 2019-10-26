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

    labels = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    hr_data = [1, 2, 3, 4, 5, 6, 7]
    rr_data = [8, 9, 10, 11, 12, 13, 14]
    return labels, hr_data, rr_data

    