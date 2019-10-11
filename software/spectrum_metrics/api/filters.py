from django.db import models
from django_filters import rest_framework as filters
from pulse_tracer.models import(
    Device,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
    User
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
            "id": ["exact", "lt", "lte"],
            "serial_number": ["exact"],
            "device_model": ["exact"]
        }


class ROIFilters(filters.FilterSet):
    class Meta:
        model = ROI
        fields = {
            "id": ["exact"],
            "location_id": ["exact"],
            "batch_id": ["exact", "lt", "lte", "gt", "gte"],
            "device": ["exact"],
            "device__id": ["exact"],
            "device__serial_number": ["exact"],
            "collection_time": ["exact", "lt", "lte", "gt", "gte"]
        }


class UserFilters(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "id": ["exact"],
            "username": ["exact"],
            "first_name": ["exact"],
            "last_name": ["exact"],
        }


class PatientFilters(filters.FilterSet):
    class Meta:
        model = Patient
        fields = {
            "id": ["exact"],
            "user__username": ["exact"],
            "user__first_name": ["exact"],
            "user__last_name": ["exact"],
            "health_care_provider__id": ["exact"],
            "health_care_provider__user__username": ["exact"],
            "health_care_provider__user__first_name": ["exact"],
            "health_care_provider__user__last_name": ["exact"],
            "device": ["exact"],
            "device__id": ["exact"],
        }


class HealthCareFilters(filters.FilterSet):
    class Meta:
        model = HealthCare
        fields = {
            "id": ["exact"],
            "user__username": ["exact"],
            "user__first_name": ["exact"],
            "user__last_name": ["exact"],
        }


class HeartRateFilters(filters.FilterSet):
    class Meta:
        model = HeartRate
        fields = {
            "patient": ["exact"],
            "patient__id": ["exact"],
            "analyzed_time": ["exact", "lt", "lte", "gt", "gte"],
            "roi": ["exact"],
            "roi__location_id": ["exact"]
        }


class RespiratoryRateFilters(filters.FilterSet):
    class Meta:
        model = RespiratoryRate
        fields = {
            "patient": ["exact"],
            "patient__id": ["exact"],
            "analyzed_time": ["exact", "lt", "lte", "gt", "gte"],
            "roi": ["exact"],
            "roi__location_id": ["exact"]
        }