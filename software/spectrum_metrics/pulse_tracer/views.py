from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
import json
import requests
from django.http import JsonResponse
from datetime import datetime,timedelta, date   
from pulse_tracer.models import Device,HeartRate,RespiratoryRate
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
import pandas as pd
import numpy as np
import pytz
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404


from .models import(
    HealthCare,
    Patient,
    User,
    Device, HeartRate, RespiratoryRate
)

from .forms import(
    UserUpdateForm,
    HealthCareUpdateForm,
    PatientUpdateForm
)
from .utils import query_scripts


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'pulse_tracer/index.html'

    def get(self, request, **kwargs):
        current_user_id = request.user.id
        user = get_object_or_404(User, id=current_user_id)
        
        '''
        if user.is_patient:
            patient = get_object_or_404(Patient, user__id=current_user_id)
            labels, data = query_scripts.get_weekly_summary(patient)
        elif user.is_health_care:
            # CHANGE THIS
            hr_labels, hr_data, rr_data = query_scripts.get_weekly_summary(user)
        context = {
            "hr_labels": hr_labels,
            "hr_data": hr_data,
            "rr_data": rr_data,
        }
        '''
        try:
            obj= HeartRate.objects.get(id=current_user_id)
            
            #Get the latest value of HR
            last_hr=HeartRate.objects.all().reverse()[0].heart_rate
            
            #Get the latest value of RR
            last_rr=RespiratoryRate.objects.all().reverse()[0].respiratory_rate
            
            #Add HR and RR value into dict for rendering
            args= {'hr':last_hr, 'rr':last_rr}
            
        #Exception if there is no corresponding user_id in db
        except:
            raise Http404("No MyModel matches the given query.")
        
        return render(request, self.template_name, args)

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
        current_user_id = request.user.id

        try:
            obj= HeartRate.objects.get(id=current_user_id)
            
            #Get 1 week from current
            today = date.today()
            week_prior =  today - timedelta(weeks=1)
            
            #Select only tuples in 7 days range
            hr = HeartRate.objects.filter(Q(analyzed_time=today,analyzed_time__gte=week_prior)|Q(analyzed_time__gt=week_prior)).order_by('analyzed_time')
            
            current_user_id = request.user.id
            user = get_object_or_404(User, id=current_user_id)
            
            #Filter query by user id       
            hr=hr.filter(id=current_user_id)
            
            #Keep only hr and corresponding collection time
            hr=hr.values('heart_rate','analyzed_time')
    
            #Put Query Set into dataframe
            df = pd.DataFrame(hr)
    
            #Round hour to floor. E.g: 22:35:00 -> 22:00:00
            df['timeStamp'] = df['analyzed_time'].dt.floor('h')
      
            #Remove analyzed_time column which haven't hour rounded 
            del df['analyzed_time']
    
            #Convert heart_rate to numeric type for computation purpose
            df['heart_rate']= df['heart_rate'].apply(pd.to_numeric)
    
            #Calculate heart rate for each hour of days
            df['avg_result'] = df.groupby(['timeStamp'])['heart_rate'].transform('mean')
            
            #Drop original heart_rate column
            del df['heart_rate']
            df=df.drop_duplicates()
    
            #Convert timeStamp to string, so we can convert dataframes to dict after
            df['timeStamp']=df['timeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    
            #Convert dataframe to dict with 'record' type (each row becomes a dictionary where key is column name and value is the data in the cell)
            data2=df.to_dict('records')
            
        #Exception if there is no corresponding user_id in db
        except:
            raise Http404("No MyModel matches the given query.")

        #Return the dict data to the chart
        return Response(data2)

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

        # TODO: Add a cancel button in the form view

        if user_update_form.is_valid() and health_care_update_form.is_valid():
            user = user_update_form.save()
            health_care_provider = health_care_update_form.save(commit=False)
            health_care_provider.user = user
            health_care_provider.save()
            return HttpResponseRedirect(reverse('health_care_provider'))

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
    
    
class PatientDetailView(LoginRequiredMixin, generic.DetailView):
    model = Patient
    template_name = 'pulse_tracer/patient_detail.html'

    def get(self, request, **kwargs):
        patient = Patient.objects.get(user__id=request.user.id)
        context = {
            'patient': patient
        }
        return render(request, self.template_name, context)
    

class PatientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Patient
    template_name = 'pulse_tracer/patient_update.html'

    def get(self, request, **kwargs):
        current_user_id = request.user.id
        user = get_object_or_404(User, id=current_user_id)
        patient = get_object_or_404(Patient, user__id=current_user_id)
        user_update_form = UserUpdateForm(instance=user)
        patient_update_form = PatientUpdateForm(instance=Patient.objects.get(user__id=current_user_id))
        context = {
            'patient': patient,
            'user_form': user_update_form,
            'patient_form': patient_update_form
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        current_user_id = request.user.id
        user = get_object_or_404(User, id=current_user_id)
        user_update_form = UserUpdateForm(request.POST, instance=user)
        patient_update_form = PatientUpdateForm(request.POST, instance=Patient.objects.get(user__id=current_user_id))
        
        # TODO: Do something about errors here
        print(user_update_form.errors)
        print(patient_update_form.errors)

        if user_update_form.is_valid() and patient_update_form.is_valid():
            user = user_update_form.save()
            patient = patient_update_form.save(commit=False)
            patient.user = user
            patient.save()
            return HttpResponseRedirect(reverse('patient'))
            
            