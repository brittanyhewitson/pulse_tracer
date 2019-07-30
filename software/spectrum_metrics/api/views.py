from rest_framework import viewsets
from .serializers import (
    DeviceSerializer,
    ROISerializer,
    ROICreateSerializer,
    PatientSerializer,
    PatientCreateSerializer,
    HealthCareSerializer,
    HeartRateSerializer,
    RespiratoryRateSerializer
)

from pulse_tracer.models import(
    Device,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
)

from api.filters import(
    DeviceFilters,
    ROIFilters,
    PatientFilters,
    HealthCareFilters,
    HeartRateFilters,
    RespiratoryRateFilters
)

# TODO: Add filters.py with all filters for each model

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_class = DeviceFilters


class ROIViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ROI.objects.all()
    serializer_class = ROISerializer
    filter_class = ROIFilters

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ROICreateSerializer
        
        return ROISerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_class = PatientFilters

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PatientCreateSerializer
        
        return PatientSerializer


class HealthCareViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = HealthCare.objects.all()
    serializer_class = HealthCareSerializer
    filter_class = HealthCareFilters


class HeartRateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = HeartRate.objects.all()
    serializer_class = HeartRateSerializer
    filter_class = HeartRateFilters


class RespiratoryRateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = RespiratoryRate.objects.all()
    serializer_class = RespiratoryRateSerializer
    filter_class = RespiratoryRateFilters