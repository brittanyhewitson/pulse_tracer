from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import Http404
import json
import requests
from django.http import JsonResponse
# Create your views here.
from pulse_tracer.models import Device,HeartRate,RespiratoryRate
from rest_framework.views import APIView
from rest_framework.response import Response
#from django_pandas.io import read_frame
from collections import defaultdict
import pytz
from django.db.models import Q
from django.shortcuts import get_object_or_404
import html
import pandas as pd
import numpy as np
from django.http import JsonResponse
from datetime import datetime,timedelta, date   
from django.http import Http404


from .models import(
    HealthCare,
    Patient,
    User,
    Device,
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
            # TODO: Change template for patient
            hr_labels, hr_data, rr_data = query_scripts.get_weekly_summary(user)
        elif user.is_health_care:
            # CHANGE THIS
            # TODO: Change template for health care provider
            hr_labels, hr_data, rr_data = query_scripts.get_weekly_summary(user)
            context = {
            "hr_labels": hr_labels,
            "hr_data": hr_data,
            "rr_data": rr_data,
        }
        '''
        #Get 7 days from today
        today = date.today()
        week_prior =  today - timedelta(weeks=1)
        print(type(week_prior))
    
        #Filter HR data for 7 day range
        lastItem = HeartRate.objects.filter(Q(analyzed_time=today,analyzed_time__gte=week_prior)|Q(analyzed_time__gt=week_prior)).order_by('analyzed_time')
        
        #Filter HR data based on ID
        lastItem=lastItem.filter(patient_id=current_user_id)
        
        #Filter RR data for 7 day range and based on ID
        lastItemRR = RespiratoryRate.objects.filter(Q(analyzed_time=today,analyzed_time__gte=week_prior)|Q(analyzed_time__gt=week_prior)).order_by('analyzed_time')
        lastItemRR = lastItemRR.filter(patient_id=current_user_id)
        print("INDEXXXXXXXXX")
        print(current_user_id)

        #Extract only 'heart_rate', and 'analyzed_time' of HR and RR
        lastItem=lastItem.values('heart_rate','analyzed_time')
        lastItemRR=lastItemRR.values('respiratory_rate','analyzed_time')
        
        #Add HR and RR to dataframes
        df = pd.DataFrame(lastItem)
        dfRR = pd.DataFrame(lastItemRR)

        #Round down timestamp. E.g: 22:45:00 -> 22:00:00
        df['timeStamp'] = df['analyzed_time'].dt.to_period('H').dt.to_timestamp()
        dfRR['timeStamp'] = dfRR['analyzed_time'].dt.to_period('H').dt.to_timestamp()

        del df['analyzed_time']
        del dfRR['analyzed_time']

        df['heart_rate']= df['heart_rate'].apply(pd.to_numeric)
        dfRR['respiratory_rate']= dfRR['respiratory_rate'].apply(pd.to_numeric)
        
        #Calculate average of HR and RR for each hour
        df['avg_result'] = df.groupby(['timeStamp'])['heart_rate'].transform('mean')
        dfRR['avg_result'] = dfRR.groupby(['timeStamp'])['respiratory_rate'].transform('mean')

        del df['heart_rate']
        del dfRR['respiratory_rate']

        df=df.drop_duplicates()
        dfRR=dfRR.drop_duplicates()

        df['timeStamp']=df['timeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        dfRR['timeStamp']=dfRR['timeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        
        data2=df.to_dict('records')
        data2RR=dfRR.to_dict('records')
        
        #Add series to list for chart
        hr_labels= df['timeStamp'].tolist()
        hr_data= df['avg_result'].tolist()
        rr_data = dfRR['avg_result'].tolist()
        
        #Extract the latest value of HR and RR based on "analyzed_time"
        last_hr=HeartRate.objects.latest('analyzed_time').heart_rate
        last_rr=RespiratoryRate.objects.latest('analyzed_time').respiratory_rate

        context = {
            "hr_labels": hr_labels,
            "hr_data": hr_data,
            "rr_data": rr_data,
            "latest_hr":int(last_hr), 
            "latest_rr":  int(last_rr)
        }
        return render(request, self.template_name, context)

class DataSummaryView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pulse_tracer/data_summary.html'

    def get(self, request, **kwargs):
        current_user_id = request.user.id
        print(current_user_id)
        
        #Get day picked for fron end or default date
        min_day= request.GET.get('datefrom') or '2019-11-01'
        max_day = request.GET.get('dateto') or '2019-11-04'
        
        print("SUMMARYYYYYYYYYYYYYYY")
        max_day= datetime.strptime(max_day, '%Y-%m-%d') #+ timedelta(days=1)
        min_day= datetime.strptime(min_day, '%Y-%m-%d')
        max_day=max_day.date()
        min_day=min_day.date()
        
        #Filter HR based on given date range
        sumHR=HeartRate.objects.filter(analyzed_time__date__range=(min_day, max_day) )
        
        #Filter HR for corresponding id
        sumHR=sumHR.filter(patient_id=current_user_id)
        sumHR=sumHR.values('heart_rate','analyzed_time')

        dfHR = pd.DataFrame(sumHR)
        
        #Turn of timezone 
        dfHR['analyzed_time']=dfHR['analyzed_time'].dt.tz_localize(None)
        print("DATAFRAME____HR___")
        print(dfHR)

        #Filter RR based on given date range
        sumRR=RespiratoryRate.objects.filter(analyzed_time__date__range=(min_day, max_day) )
        
        #Filter HR for corresponding id
        sumRR=sumRR.filter(patient_id=current_user_id)
        sumRR=sumRR.values('respiratory_rate','analyzed_time')
        dfRR = pd.DataFrame(sumRR)
        
        dfRR['analyzed_time']=dfRR['analyzed_time'].dt.tz_localize(None)
 
        #Round down timestamp. E.g: 22:45:00 -> 22:00:00
        dfHR['timeStamp'] = dfHR['analyzed_time'].dt.to_period('H').dt.to_timestamp()
        dfRR['timeStamp'] = dfRR['analyzed_time'].dt.to_period('H').dt.to_timestamp()

        del dfHR['analyzed_time']
        del dfRR['analyzed_time']

        dfHR['heart_rate']= dfHR['heart_rate'].apply(pd.to_numeric)
        dfRR['respiratory_rate']= dfRR['respiratory_rate'].apply(pd.to_numeric)
        
        #Calculate average of HR and RR for each hour
        dfHR['avg_result'] = dfHR.groupby(['timeStamp'])['heart_rate'].transform('mean')
        dfRR['avg_result'] = dfRR.groupby(['timeStamp'])['respiratory_rate'].transform('mean')
  
        del dfHR['heart_rate']
        del dfRR['respiratory_rate']

        dfHR=dfHR.drop_duplicates()
        dfRR=dfRR.drop_duplicates()

        dfHR['timeStamp']=dfHR['timeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        dfRR['timeStamp']=dfRR['timeStamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()

        hr_labels= dfHR['timeStamp'].tolist()
        hr_data= dfHR['avg_result'].tolist()
        rr_data = dfRR['avg_result'].tolist()
        context = {}
        context = {
            "hr_labels": hr_labels,
            "hr_data": hr_data,
            "rr_data": rr_data,
        }

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
        #patient = Patient.objects.get(user__id=request.user.id)
        print("TESTT")
        print(request.user.id)
        patient = get_object_or_404(Patient, user__id=request.user.id)
        context = {
            'patient': patient
        }
        print("TEST2")
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
            
class ChartDataRR(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
        #id=IndexView.get.user__id
        try:
            #current_user_id = request.user.id
            test={'current_user_id':5}
        except:
            raise Http404("No MyModel matches the given query.")
        return Response(test)