from rest_framework import serializers
from pulse_tracer.models import(
    Device,
    ROI,
    Patient,
    HealthCare,
    HeartRate,
    RespiratoryRate,
    User,
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name"
        ]


class HealthCareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthCare
        fields = "__all__"


class HealthCareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCare
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    health_care_provider = HealthCareSerializer(many=True, read_only=True)
    device = DeviceSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
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