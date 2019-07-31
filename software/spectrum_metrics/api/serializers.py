from rest_framework import serializers
from pulse_tracer.models import(
    Device,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class ROISerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    
    class Meta:
        model = ROI
        fields = "__all__"


class ROICreateSerializer(serializers.ModelSerializer):   
    class Meta:
        model = ROI
        fields = "__all__"


class HealthCareSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCare
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    health_care_provider = HealthCareSerializer(many=True, read_only=True)
    device = DeviceSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = "__all__"


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class HeartRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRate
        fields = "__all__"


class RespiratoryRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespiratoryRate
        fields = "__all__"