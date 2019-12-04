from django import forms
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus import DatePickerInput

from pulse_tracer.models import(
    User,
    HealthCare,
    Patient,
    Device
)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        help_text='Optional.'
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        help_text='Optional.'
    )
    email = forms.EmailField(
        max_length=254, 
        help_text='Required. Inform a valid email address.'
    )
    user_type = forms.ChoiceField(
        choices=[
            ("P", "Patient"),
            ("HC", "Health Care Provider"),
        ], 
    )

    class Meta:
        model = User
        fields = (
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2', 
        )


class CreatePatientForm(forms.ModelForm):
    weight = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Weight in kg.'
    )
    height = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Height in cm.'
    )
    class Meta:
        model = Patient
        fields = [
            'birth_date',
            'gender',
            'weight',
            'height',
            'health_conditions',
            'health_care_provider',
        ]

        widgets = {
            'birth_date': DatePickerInput(format='%m/%d/%Y')
        }


class CreateHealthCareForm(forms.ModelForm):
    class Meta:
        model = HealthCare
        fields = [
            'role',
        ]


class CreateDeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'device_model',
            'serial_number',
        ]