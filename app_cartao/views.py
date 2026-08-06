from django.shortcuts import render
from django.views.generic           import TemplateView


class CartaoView(TemplateView):
    template_name = 'app_cartao/cartao.html'
