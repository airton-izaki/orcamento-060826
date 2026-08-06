
from django.contrib import admin
from django.urls import path

from app_home.views             import HomeView
from app_despesa.views          import DespesaView
from app_cartao.views           import CartaoView










urlpatterns = [
    path('admin/', admin.site.urls),

    path('',                        HomeView.as_view(),                             name = 'index'),

    path('despesa/',                DespesaView.as_view(),                          name = 'despesa'),






    path('cartao/',                  CartaoView.as_view(),                          name = 'cartao' ),
]
