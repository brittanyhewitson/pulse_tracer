from rest_framework import viewsets
from .serializers import (
    DeviceSerializer,
    BatchSerializer,
    ROISerializer,
    ROICreateSerializer,
    PatientSerializer,
    PatientCreateSerializer,
    HealthCareSerializer,
    HealthCareCreateSerializer,
    HeartRateSerializer,
    RespiratoryRateSerializer,
    UserSerializer
)

from pulse_tracer.models import(
    Device,
    Batch,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
    User
)

from api.filters import(
    DeviceFilters,
    BatchFilters,
    ROIFilters,
    PatientFilters,
    HealthCareFilters,
    HeartRateFilters,
    RespiratoryRateFilters,
    UserFilters,
)

# TODO: Add filters.py with all filters for each model

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_class = DeviceFilters


class BatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    filter_class = BatchFilters


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
    class Meta:
        ordering = ['-id']
    queryset = HealthCare.objects.all()
    serializer_class = HealthCareSerializer
    filter_class = HealthCareFilters

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HealthCareCreateSerializer

        return HealthCareSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = UserFilters


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