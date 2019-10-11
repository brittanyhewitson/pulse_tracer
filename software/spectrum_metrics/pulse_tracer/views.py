from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse


from .models import(
    HealthCare,
    Patient,
    User,
    Device,
)


class IndexView(generic.ListView):
    template_name = 'pulse_tracer/index.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class DataSummaryView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pulse_tracer/data_summary.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


# TODO: User permission required mixin here
class HealthCareProviderDetailView(LoginRequiredMixin, generic.DetailView):
    model = HealthCare
    template_name = 'pulse_tracer/health_care_provider_detail.html'

    def get(self, request, **kwargs):
        health_care_provider = HealthCare.objects.get(user__id=request.user.id)
        context = {
            'health_care_provider': health_care_provider
        }
        return render(request, self.template_name, context)


class PatientListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pulse_tracer/patient_list.html'

    def get(self, request, **kwargs):
        patients = Patient.objects.filter(health_care_provider__user__id=request.user.id)
        for patient in patients:
            print(patient)
        context = {
            'patients': patients
        }
        return render(request, self.template_name, context)
