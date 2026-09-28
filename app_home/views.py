from django.shortcuts import render
from django.contrib import messages
from django.views.generic       import TemplateView
from django.db.models               import Sum
from datetime                   import date
from app_despesa.models         import Despesa, Grupo, DespesaParcelaCartao
from app_investimento.models    import InvestimentoCreate
from app_receita.models         import Receita




class HomeView (TemplateView):
    template_name = 'app_home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()

        # 1. Captura as strings da URL
        mes_raw = self.request.GET.get('mes')
        ano_raw = self.request.GET.get('ano', str(hoje.year))

        # 2. Limpa qualquer caractere que não seja número
        ano_limpo = ''.join(filter(str.isdigit, ano_raw))

        # 3. FORÇA A CONVERSÃO PARA INTEIRO (Crucial para o ORM do Django)
        try:
            mes_selecionado = int(mes_raw)
        except (TypeError, ValueError):
            mes_selecionado = hoje.month
            if mes_raw is not None:
                messages.error(self.request, 'Digite um mês válido (de 1 a 12).')

        ano_selecionado = int(ano_limpo) if ano_limpo else int(hoje.year)

        if not 1 <= mes_selecionado <= 12:
            mes_selecionado = hoje.month
            messages.error(self.request, 'Digite um mês válido (de 1 a 12).')

        meses_ano = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        context['mes'] = meses_ano[mes_selecionado]

        context['mes_atual'] = mes_selecionado
        context['ano_atual'] = ano_selecionado
        context['lista_anos'] = range(hoje.year - 2, hoje.year + 3)

        #  CARTÃO 1: Despesa (Filtrado pelo mês atual)
        total_despesas_normais = Despesa.objects.exclude(forma_pagamento = 'CARTAO').filter(
            data__year = ano_selecionado,
            data__month = mes_selecionado
        ).aggregate(total=Sum('valor'))['total'] or 0

        # Parcelas de Cartão vencendo no mês
        total_parcelas_cartao = DespesaParcelaCartao.objects.filter(
            data_vencimento__year = ano_selecionado,
            data_vencimento__month = mes_selecionado
        ).aggregate(total=Sum('valor_parcela'))['total'] or 0

        # Soma tudo para o cartão de despesas totais
        context['total_despesas_filtradas'] = total_despesas_normais + total_parcelas_cartao

        #  CARTÃO 2: Receita (Filtrado pelo mês atual)
        context['total_receitas_filtradas'] = Receita.objects.filter(
            data_recebimento__year = ano_selecionado,
            data_recebimento__month = mes_selecionado
        ).aggregate(total = Sum('valor'))['total'] or 0

        #  CARTÃO 3: Cartão de Crédito (Filtrado pelo mês atual)
        context['total_cartao_mes'] = total_parcelas_cartao

        #  CARTÃO 4: Investimento (Filtrado pelo mês atual)
        context['total_investimentos'] = InvestimentoCreate.objects.filter(
            data_aplicacao__year = ano_selecionado,
            data_aplicacao__month = mes_selecionado,
        ).aggregate(total = Sum('valor_inicial'))['total'] or 0

        context['lista_grupos'] = Grupo.objects.all()

        return context
