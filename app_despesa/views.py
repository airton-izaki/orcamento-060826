from django.shortcuts import render

from django.views.generic           import TemplateView


class DespesaView(TemplateView):
    template_name = 'app_despesa/despesa.html'
