from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Device(models.Model):
    # Device ID (PK)

    # Model
    device_model = models.CharField(
        max_length=100,
        blank=False
    )

    serial_number = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
    )

    def __str__(self):
        return "_".join(["PT", format(self.id, "04")])


class ROI(models.Model):
    # ROI ID (PK)

    # Location ID choices
    LOCATION_ID_CHOICES = [
        ("31", "Right Cheek"),
        ("35", "Left Cheek"),
    ]
    # Location ID
    location_id = models.CharField(
        max_length=100,
        choices=LOCATION_ID_CHOICES,
        blank=False,
    )

    # Data
    data = models.TextField()

    # Collection Time
    collection_time = models.DateTimeField(
        blank=False,
    )

    # Device ID (FK)
    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    # Patient ID (FK)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["ROI", format(self.id, "04")])


class Patient(models.Model):
    # Patient ID (PK)

    # Name
    name = models.CharField(
        max_length=100
    )

    # Date of Birth
    birth_date = models.DateField(
        blank=False,
    )

    # TODO: some sort of convention for lbs or kgs
    # Weight (in kg)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    # TODO: some sort of convention for ft or m
    # Height (in cm)
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    # Health Conditions
    health_conditions = models.TextField(
    )

    # Device ID (FK)
    device = models.OneToOneField(
        "Device",
        on_delete=models.CASCADE
    )

    # Health Care Provider (FK)
    health_care_provider = models.ManyToManyField(
        'HealthCare'
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["P", format(self.id, "04")])


class HealthCare(models.Model):
    # Health Care ID (PK)

    ROLE_CHOICES = [
        ("RN", "Registered Nurse"),
        ("PHYS", "Physician"),
        ("PHARM", "Pharmacist"),
        ("RT", "Respiratory Therapist"),
    ]

    # Name
    name = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        blank=False,
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["HC", format(self.id, "04")])


class HeartRate(models.Model):
    # Heart Rate ID (PK)

    # Heart Rate Number
    heart_rate = models.DecimalField(
        blank=True,
        max_digits=5,
        decimal_places=2,
    )

    # Data
    data = models.TextField()

    # Collection Time
    collection_time = models.DateTimeField(
        blank=False,
    )

    # Patient ID (FK)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
    )

    # ROI (FK)
    roi = models.ForeignKey(
        "ROI",
        on_delete=models.CASCADE
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["HR", format(self.id, "04")])


class RespiratoryRate(models.Model):
    # Respiratory Rate ID (PK)

    # Respiratory Rate Number
    respiratory_rate = models.DecimalField(
        blank=True,
        max_digits=5,
        decimal_places=2,
    )

    # Data
    data = models.TextField()

    # Collection Time
    collection_time = models.DateTimeField(
        blank=False,
    )

    # Patient ID (FK)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
    )

    # ROI (FK)
    roi = models.ForeignKey(
        "ROI",
        on_delete=models.CASCADE
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["RR", format(self.id, "04")])
