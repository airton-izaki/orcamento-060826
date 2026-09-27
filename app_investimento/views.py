from django.shortcuts                                  import render
from django.http                                       import JsonResponse
from django.db.models                                  import Sum
from django.views.generic                              import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.urls                                       import reverse, reverse_lazy
from app_investimento.models                           import InvestimentoCreate
from app_investimento.forms.investimentocreateform     import InvestimentoCreateForm


# ────────────────────────────────────────────────────────────────────────────────
# Investimento 
# ────────────────────────────────────────────────────────────────────────────────
class InvestimentoView(ListView):
    model = InvestimentoCreate
    template_name = 'app_investimento/investimento.html'
    context_object_name = 'investimentos'

    def get_queryset(self):
        queryset = InvestimentoCreate.objects.all().order_by('-data_aplicacao')  
        
        self.data_aplicacao = self.request.GET.get('data_aplicacao')    
        self.data_vencimento = self.request.GET.get('data_vencimento')

        if self.data_aplicacao:
            queryset = queryset.filter(data_aplicacao__gte = self.data_aplicacao)

        if self.data_vencimento:
            queryset = queryset.filter(data_vencimento__lte = self.data_vencimento)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_filtrado = self.get_queryset().aggregate(total = Sum('saldo_atual'))['total'] or 0

        context['total_filtrado'] = total_filtrado
        context['data_aplicacao_atual'] = self.data_aplicacao or ''
        context['data_vencimento_atual'] = self.data_vencimento or ''

        return context









# ────────────────────────────────────────────────────────────────────────────────
# Investimento - Criar
# ────────────────────────────────────────────────────────────────────────────────
class InvestimentoCreateView(CreateView):
    model = InvestimentoCreate
    form_class = InvestimentoCreateForm
    template_name = 'app_investimento/investimentocriar.html'
    success_url = reverse_lazy('investimento')

    def form_valid(self, form):
        self.object = form.save()

        return JsonResponse({
            'status': 'sucesso',
            'titulo': 'Sucesso',
            'mensagem': 'Investimento cadastrado com sucesso.',
            'redirect_url': str(self.success_url)
        })

    def form_invalid(self, form):
        return JsonResponse({
            'status': 'erro',
            'titulo': 'Erro',
            'mensagem': form.errors.as_ul()
         }, status = 400)

# ────────────────────────────────────────────────────────────────────────────────
# Investimento - Resumo
# ────────────────────────────────────────────────────────────────────────────────
class InvestimentoResumoView(TemplateView):
    template_name = 'app_investimento/investimentoresumo.html'























