from django.shortcuts import render, get_object_or_404, redirect
from django.contrib                         import messages
from django.db.models                       import Sum
from django.http                            import JsonResponse
from django.urls                            import reverse_lazy
from django.views.generic                   import TemplateView, CreateView, ListView, UpdateView, DeleteView
from .models                                import Receita

from app_receita.forms.receitaform          import ReceitaForm

# ─────────────────────────────────────────────────────────────────────────────────
# Receita
# ─────────────────────────────────────────────────────────────────────────────────
class ReceitaView(ListView):
    model = Receita
    template_name = 'app_receita/receita.html'
    context_object_name = 'receitas'

    def get_queryset(self):
        queryset = (Receita.objects.select_related('usuario'))

        # Filtro por categoria
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria = categoria)

        # Filtro por fonte pagadora
        fonte = self.request.GET.get('fonte')
        if fonte:
            queryset = queryset.filter(fonte__icontains = fonte)

        # Filtro por data inicial
        data_inicial = self.request.GET.get('data_inicial')
        if data_inicial:
            queryset = queryset.filter(data_recebimento__gte = data_inicial)

        # Filtro por data final
        data_final = self.request.GET.get('data_final')
        if data_final:
            queryset = queryset.filter(data_recebimento__lte = data_final)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receitas = context['receitas']

        # Total das receitas exibidas após os filtros
        context['total_receita'] = (receitas.aggregate(
            total = Sum('valor')
        )['total'] or 0)

        # Quantidade de receitas
        context['quantidade_receita'] = receitas.count()

        # Valores dos filtros
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['data_inicial'] = self.request.GET.get('data_inicial', '')
        context['data_final'] = self.request.GET.get('data_final', '')

        # Opções do campo categoria
        context['categoria'] = Receita.CHOICE_CATEGORIA

        return context









# ─────────────────────────────────────────────────────────────────────────────────
# Receita - Criar
# ─────────────────────────────────────────────────────────────────────────────────
class ReceitaCreateView(CreateView):
    model = Receita
    form_class = ReceitaForm
    template_name = 'app_receita/receitacreate.html'
    success_url = reverse_lazy('receita')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = None
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Receita cadastrada com sucesso!")
        return JsonResponse({
            'status': 'sucesso',
            'titulo': 'Sucesso!',
            'message': 'Receita cadastrada com sucesso!',
            'redirect_url': str(self.success_url)
        })

    def form_invalid(self, form):
        messages.error(self.request, "Confira os dados preenchidos.")
        errors = form.errors.get_json_data()

        if 'data_recebimento' in errors:
            mensagem_alerta = errors['data_recebimento'][0]['message']

        else:
            mensagem_alerta = 'Por favor, verifique os campos destacados em vermelho.'

        return JsonResponse({
            'status': 'erro',
            'titulo': 'Ops! Algo deu errado',
            'mensagem': mensagem_alerta,
            'errors': errors,
        }, status = 400)


# ─────────────────────────────────────────────────────────────────────────────────
# Receita - Editar
# ─────────────────────────────────────────────────────────────────────────────────
class ReceitaUpdateView(UpdateView):
    model = Receita
    form_class = ReceitaForm
    template_name = 'app_receita/receitacreate.html'
    success_url = reverse_lazy('receita')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        messages.success(self.request, "Receita autalizada com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Confira os dados preenchidos.")
        return super().form_invalid(form)




# ─────────────────────────────────────────────────────────────────────────────────
# Receita - Editar
# ─────────────────────────────────────────────────────────────────────────────────
class ReceitaDeleteView(DeleteView):
    model = Receita
    template_name = 'app_receita/receitadelete.html'
    success_url = reverse_lazy('receita')
    success_message = "Receita '%(descricao)s' deletada com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Excluir Receita'
        context['icone'] = 'bi bi-exclamation-triangle'
        context['cancelar_url'] = reverse_lazy('receita')

        return context



