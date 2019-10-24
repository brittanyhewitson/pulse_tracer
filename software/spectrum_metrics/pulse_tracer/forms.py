from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import(
    User,
    HealthCare,
)


class UserUpdateForm(forms.ModelForm):
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

    class Meta:
        model = User
        fields = [
            #'username', 
            'first_name', 
            'last_name', 
            'email', 
        ]


class HealthCareUpdateForm(forms.ModelForm):
    class Meta:
        model = HealthCare
        fields = [
            'role'
        ]
