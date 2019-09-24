from django.shortcuts import render
from django.views import generic

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'pulse_tracer/index.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class DataSummaryView(generic.TemplateView):
    template_name = 'pulse_tracer/data_summary.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class HealthCareProviderDetail(generic.TemplateView):
    template_name = 'pulse_tracer/health_care_provider_detail.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)