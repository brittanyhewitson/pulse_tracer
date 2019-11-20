from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse


from pulse_tracer.models import(
    HealthCare,
    Patient,
    User,
    Device,
)

from .forms import(
    CreatePatientForm,
    CreateHealthCareForm,
    SignUpForm,
    CreateDeviceForm,
)


# Authentication Views
class SignUpView(generic.TemplateView):
    template_name = 'registration/signup.html'

    def get(self, request, **kwargs):
        signup_form = SignUpForm()
        context = {
            'form': signup_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        signup_form = SignUpForm(request.POST)

        if signup_form.is_valid():
            signup_form.save()
            username = signup_form.cleaned_data.get('username')
            raw_password = signup_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            if signup_form.cleaned_data.get('user_type') == "HC":
                user.is_health_care = True
                user.save()
                return HttpResponseRedirect(reverse('create_health_care', args=(user.id, )))
            elif signup_form.cleaned_data.get('user_type') == "P":
                user.is_patient = True
                user.save()
                return HttpResponseRedirect(reverse('create_device', kwargs={'pk': user.id}))


class CreateDeviceView(generic.TemplateView):
    template_name = 'registration/create_device.html'

    def get(self, request, **kwargs):
        device_form = CreateDeviceForm()
        context = {
            'form': device_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        device_form = CreateDeviceForm(request.POST)

        # TODO: Add error checking here. i.e. if device with invalid serial number
        # exists or if device with that serial number already exists
        if device_form.is_valid():
            device = device_form.save()

            return HttpResponseRedirect(reverse('create_patient', kwargs={'pk': kwargs["pk"], 'device_id': device.id}))
        #print(device_form.errors)

# TODO: Add errors
class CreatePatientView(generic.TemplateView):
    template_name = 'registration/create_patient.html'

    def get(self, request, **kwargs):
        patient_form = CreatePatientForm()
        user = get_object_or_404(User, pk=kwargs["pk"])
        context = {
            'user_type': 'Patient',
            'form': patient_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        patient_form = CreatePatientForm(request.POST)
        
        if patient_form.is_valid():
            user = get_object_or_404(User, pk=kwargs["pk"])
            #user.is_patient = True
            #user.save()
            device = get_object_or_404(Device, pk=kwargs["device_id"])
            patient = patient_form.save(commit=False)
            patient.user = user
            patient.device = device
            patient.save()

            health_care_providers = patient_form.cleaned_data.get('health_care_provider')
            for health_care_provider in health_care_providers:
                health_care_provider = HealthCare.objects.get(pk=health_care_provider.id)
                patient.health_care_provider.add(health_care_provider)
            patient.save()
        return HttpResponseRedirect(reverse("index"))


class CreateHealthCareView(generic.TemplateView):
    template_name = 'registration/create_health_care.html'

    def get(self, request, **kwargs):
        health_care_form = CreateHealthCareForm()
        user = get_object_or_404(User, **kwargs)
        context = {
            'user_type': 'Health Care Provider',
            'form': health_care_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        health_care_form = CreateHealthCareForm(request.POST)
        
        if health_care_form.is_valid():
            user = get_object_or_404(User, **kwargs)
            user.is_health_care = True
            user.save()
            health_care = health_care_form.save(commit=False)
            health_care.user = user
            health_care.save()
        return HttpResponseRedirect(reverse("index"))

        
def logout_view(request):
    logout(request)
    msg = "Successfully logged out"
    messages.info(request, msg)
    return HttpResponseRedirect(reverse("login"))
