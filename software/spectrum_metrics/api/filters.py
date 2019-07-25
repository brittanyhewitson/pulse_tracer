from django.db import models
from django_filters import rest_framework as filters
from pulse_tracer.models import(
    Device,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
)

class BaseFilterSet(filters.FilterSet):
    # Relational fields have a text input box in the browser
    class Meta:
        filter_overrides = {
            models.ForeignKey: {"filter_class": filters.CharFilter},
            models.ManyToManyField: {"filter_class": filters.CharFilter},
            models.OneToOneField: {"filter_class": filters.CharFilter}
        }

class DeviceFilters(filters.FilterSet):
    class Meta:
        model = Device
        fields = {
            "id": ["exact"],
            "serial_number": ["exact"],
            "device_model": ["exact"]
        }


class ROIFilters(filters.FilterSet):
    class Meta:
        model = ROI
        fields = {
            "id": ["exact"],
            "location_id": ["exact"],
            "device__id": ["exact"],
            "device__serial_number": ["exact"],
            "patient__id": ["exact"]
        }


class PatientFilters(filters.FilterSet):
    class Meta:
        model = Patient
        fields = {
            "id": ["exact"],
            "name": ["exact"],
            "health_care_provider__id": ["exact"],
            "health_care_provider__name": ["exact"],
        }


class HealthCareFilters(filters.FilterSet):
    class Meta:
        model = HealthCare
        fields = {
            "id": ["exact"],
            "name": ["exact"],
            "patient__id": ["exact"]
        }


class HeartRateFilters(filters.FilterSet):
    class Meta:
        model = HeartRate
        fields = {
            "patient__id": ["exact"],
            "collection_time": ["exact"],
            "roi__location_id": ["exact"]
        }


class RespiratoryRateFilters(filters.FilterSet):
    class Meta:
        model = RespiratoryRate
        fields = {
            "patient__id": ["exact"],
            "collection_time": ["exact"],
            "roi__location_id": ["exact"]
        }