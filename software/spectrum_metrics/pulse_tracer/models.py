from django.db import models
from django.contrib.auth.models import AbstractUser

ANALYSIS_CHOICES = [
    ("MD", "Matrix Decomposition"),
    ("FDBSS", "Fourier Domain Blind Source Separation")
]

LOCATION_ID_CHOICES = [
    ("31", "Right Cheek"),
    ("35", "Left Cheek"),
    ("27", "Upper Nose"),
    ("28", "Mid-Upper Nose"),
    ("29", "Mid-Lower Nose"),
    ("30", "Lower Nose"),
    ("17", "Left Outer Brow"),
    ("18", "Left Mid-Outer Brow"),
    ("19", "Left Mid Brow"),
    ("20", "Left Mid-Inner Brow"),
    ("21", "Left Inner Brow"),
    ("22", "Right Inner Brow"),
    ("23", "Right Mid-Inner Brow"),
    ("24", "Right Mid Brow"),
    ("25", "Right Mid-Outer Brow"),
    ("26", "Right Outer Brow"),
]

ROLE_CHOICES = [
    ("RN", "Registered Nurse"),
    ("PHYS", "Physician"),
    ("PHARM", "Pharmacist"),
    ("RT", "Respiratory Therapist"),
]

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
]

# Create your models here.
class Device(models.Model):
    # Device ID (PK)

    # Model
    device_model = models.CharField(
        max_length=100,
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
    )

    def __str__(self):
        return "_".join(["PT", format(self.id, "04")])


class Batch(models.Model):
    # Time the batch was created
    creation_time = models.DateTimeField(
        auto_now=False,
    )

    # Preprocessing analysis type
    preprocessing_analysis = models.CharField(
        max_length=100,
        choices=ANALYSIS_CHOICES,
    )

    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["B", format(self.id, "05")])


class ROI(models.Model):
    # ROI ID (PK)

    # Location ID
    location_id = models.CharField(
        max_length=100,
        choices=LOCATION_ID_CHOICES,
    )

    # Batch ID
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.CASCADE
    )
    
    # Data
    red_data = models.TextField()
    blue_data = models.TextField()
    green_data = models.TextField()
    
    # Collection Time
    collection_time = models.DateTimeField(
        auto_now=True,
    )

    # Analyzed by the Heart Rate Algorithm
    hr_analyzed = models.BooleanField(
        default=False
    )

    # Analyzed by the Respiratory Rate Algorithm
    rr_analyzed = models.BooleanField(
        default=False
    )

    # Currently being analyzed
    analysis_in_progress = models.BooleanField(
        default=False
    )

    # Device ID (FK)
    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    preprocessing_analysis = models.CharField(
        max_length=100,
        choices=ANALYSIS_CHOICES,
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["ROI", format(self.id, "05")])


class User(AbstractUser):
    class Meta:
        ordering = ['id']

    is_patient = models.BooleanField(default=False)
    is_health_care = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'


class Patient(models.Model):

    # Patient ID (PK)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
    )
    
    # Date of Birth
    birth_date = models.DateField(
    )

    # Gender
    gender = models.CharField(
        max_length=100,
        choices=GENDER_CHOICES,
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

    # Current Medications

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
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        #primary_key=True
    )

    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
    )

    # When the object PK is displayed
    def __str__(self):
        return " ".join([self.user.first_name, self.user.last_name])


class HeartRate(models.Model):
    # Heart Rate ID (PK)

    # Heart Rate Number
    heart_rate = models.DecimalField(
        blank=True,
        max_digits=5,
        decimal_places=2,
    )

    # Data
    data = models.TextField(
        blank=True,
        null=True
    )

    # Collection Time
    analyzed_time = models.DateTimeField(
        auto_now=True,
    )

    # Patient ID (FK)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
    )

    # ROI (FK)
    # TODO: Use the following once windowing is introduced
    '''
    roi = models.ForeignKey(
        "ROI",
        on_delete=models.CASCADE
    )
    '''
    # TODO: Remove once we introduce windowing?
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.CASCADE,
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
    data = models.TextField(
        blank=True,
        null=True
    )

    # Collection Time
    analyzed_time = models.DateTimeField(
        auto_now=True,
    )

    # Patient ID (FK)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
    )

    # ROI (FK)
    # TODO: Use the following once windowing is introduced?
    '''
    roi = models.ForeignKey(
        "ROI",
        on_delete=models.CASCADE
    )
    '''
    # TODO: Remove once we introduce windowing?
    # Batch (FK)
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.CASCADE
    )

    # When the object PK is displayed
    def __str__(self):
        return "_".join(["RR", format(self.id, "04")])
