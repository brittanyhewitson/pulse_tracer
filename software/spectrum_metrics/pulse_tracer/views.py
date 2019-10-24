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

from .forms import(
    UserUpdateForm,
    HealthCareUpdateForm,
)


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'pulse_tracer/index.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class DataSummaryView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pulse_tracer/data_summary.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


# TODO: User permission required mixin here?
class HealthCareProviderDetailView(LoginRequiredMixin, generic.DetailView):
    model = HealthCare
    template_name = 'pulse_tracer/health_care_provider_detail.html'

    def get(self, request, **kwargs):
        health_care_provider = get_object_or_404(HealthCare, user__id=request.user.id)
        context = {
            'health_care_provider': health_care_provider,
        }
        return render(request, self.template_name, context)


class HealthCareProviderUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = HealthCare
    template_name = 'pulse_tracer/health_care_provider_update.html'

    def get(self, request, **kwargs):
        current_user_id = request.user.id
        user = get_object_or_404(User, id=current_user_id)
        health_care_provider = get_object_or_404(HealthCare, user__id=current_user_id)
        user_update_form = UserUpdateForm(instance=user)
        health_care_update_form = HealthCareUpdateForm(instance=HealthCare.objects.get(user__id=current_user_id))
        context = {
            'health_care_provider': health_care_provider,
            'user_form': user_update_form,
            'healthcare_form': health_care_update_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        current_user_id = request.user.id
        user = get_object_or_404(User, id=current_user_id)
        user_update_form = UserUpdateForm(request.POST, instance=user)
        health_care_update_form = HealthCareUpdateForm(request.POST, instance=HealthCare.objects.get(user__id=current_user_id))
        
        # TODO: Do something about errors here
        print(user_update_form.errors)
        print(health_care_update_form.errors)

        if user_update_form.is_valid() and health_care_update_form.is_valid():
            user = user_update_form.save()
            health_care_provider = health_care_update_form.save(commit=False)
            health_care_provider.user = user
            health_care_provider.save()
            return HttpResponseRedirect(reverse('health_care_provider'))
        


# TODO: User permission required mixin here?
class PatientListView(LoginRequiredMixin, generic.ListView):
    template_name = 'pulse_tracer/patient_list.html'

    def get(self, request, **kwargs):
        patients = Patient.objects.filter(health_care_provider__user__id=request.user.id)
        context = {
            'patients': patients
        }
        return render(request, self.template_name, context)
