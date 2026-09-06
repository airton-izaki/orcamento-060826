
from django.contrib import admin
from django.urls import path

from app_home.views             import HomeView
from app_despesa.views          import (DespesaListView, DespesaGrupoView, EspecieCreateView, 
                                        DespesaCreateView, buscar_especies, DespesaUpdateView,
                                        DespesaDeleteView, DespesaResumoView)
from app_cartao.views           import CartaoView, CartaoCreateView, CartaoListarView, CartaoFaturaView, SelecionarFaturaView


from app_receita.views          import ReceitaView, ReceitaCreateView, ReceitaUpdateView, ReceitaDeleteView



urlpatterns = [
    path('admin/', admin.site.urls),

    path('',                            HomeView.as_view(),             name = 'index'),

    path('despesa/',                    DespesaListView.as_view(),      name = 'despesa'),
    path('despesa/Grupo/criar/',        DespesaGrupoView.as_view(),     name = 'criar_grupo'),
    path('despesa/Especie/Criar/',      EspecieCreateView.as_view(),    name = 'criar_especie'),
    path('despesa/criar/',              DespesaCreateView.as_view(),    name = 'criar_despesa'),
    path('buscar-especies/',            buscar_especies,                name = 'buscar_especies'),
    path('despesa/editar/<int:pk>/',    DespesaUpdateView.as_view(),    name = 'editar_despesa'),
    path('despesa/deletar/<int:pk>/',   DespesaDeleteView.as_view(),    name = 'deletar_despesa'),
    path('despesa/resumo/',             DespesaResumoView.as_view(),  name = 'despesa_resumo'),

    path('cartao/',                     CartaoView.as_view(),            name = 'cartao' ),
    path('cartao/criar/',               CartaoCreateView.as_view(),      name = 'criar_cartao'),
    path('cartao/listar/',              CartaoListarView.as_view(),       name = 'listar_cartao'),
    path('cartao/Fatura/',              CartaoFaturaView.as_view(),       name = 'fatura'),
    path('cartao/selecionar_fatura/',   SelecionarFaturaView.as_view(), name = 'selecionar_fatura'),


    path('receita/',                    ReceitaView.as_view(),              name = 'receita'),
    path('receita/criar/',              ReceitaCreateView.as_view(),        name = 'criar_receita'),
    path('receita/update/<int:pk>/',    ReceitaUpdateView.as_view(),        name = 'editar_receita'),
    path('receita/delete/<int:pk>/',    ReceitaDeleteView.as_view(),        name = 'deletar_receita')

]
