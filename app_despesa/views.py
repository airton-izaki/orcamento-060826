from datetime                               import date
from decimal                                import Decimal
from collections                            import defaultdict
from itertools                              import chain
from dateutil.relativedelta                 import relativedelta
from django                                 import forms
from django.shortcuts                       import render, get_object_or_404, redirect
from django.views.generic                   import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.http                            import JsonResponse, HttpResponseRedirect
from django.urls                            import reverse_lazy
from django.db                              import IntegrityError, transaction
from django.db.models                       import Sum
from django.core.exceptions                 import ValidationError


from app_despesa.models                     import Grupo, Especie, Despesa
from app_despesa.forms.GrupoForm            import DespesaGrupoForm
from app_despesa.forms.EspecieCreateForm    import EspecieCreateForm
from app_despesa.forms.despesacreateform    import DespesaForm
from app_cartao.models                      import DespesaParcelaCartao
class DespesaView(TemplateView):
    template_name = 'app_despesa/despesa.html'


# ───────────────────────────────────────────────────────────────────────────
# Grupo
# ───────────────────────────────────────────────────────────────────────────
class DespesaGrupoView(CreateView):
    model = Grupo
    form_class = DespesaGrupoForm
    template_name = 'app_despesa/GrupoCreate.html'
    success_url = reverse_lazy('despesa')

    def _is_ajax_request(self):
        return (
            self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in self.request.headers.get('Accept', '')
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        if self._is_ajax_request():
            return JsonResponse({
                'status': 'sucesso',
                'titulo': 'Grupo Criado!',
                'mensagem': 'Grupo de despesas criado com sucesso!!'
            })

        return response

    def form_invalid(self, form):
        if self._is_ajax_request():
            erros_finais = [
                f"{campo}: {', '.join(erros)}"
                for campo, erros in form.errors.items()
            ]
       
            return JsonResponse({
                'status': 'erro',
                'mensagem': '<br>'.join(erros_finais)
            },  status = 400)
    
        return super().form_invalid(form)

# ───────────────────────────────────────────────────────────────────────────
# Espécie
# ───────────────────────────────────────────────────────────────────────────
class EspecieCreateView(CreateView):
    model = Especie
    form_class = EspecieCreateForm
    template_name = 'app_despesa/EspecieCreate.html'
    success_url = reverse_lazy('despesa')

    def _is_ajax_request(self):
        return (
            self.request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or 'application/json' in self.request.headers.get('Accept', '')
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        if self._is_ajax_request():
            return JsonResponse({
                'status': 'sucesso',
                'titulo': 'Espécie criada!',
                'mensagem': 'Espécie de despesas criada com sucesso!'
            })

        return response

    def form_invalid(self, form):
        if self._is_ajax_request():
            erros_finais = [
                f"{campo}: {', '.join(erros)}" 
                for campo, erros in form.errors.items()
            ]

            return JsonResponse({
                'status': 'erro',
                'mensagem': '<br>'.join(erros_finais)
            }, status = 400)

        return super().form_invalid(form)


# ────────────────────────────────────────────────────────────────────────────────
# Despesa - Listar
# ────────────────────────────────────────────────────────────────────────────────
class DespesaListView(ListView):
    template_name = 'app_despesa/despesa.html'
    context_object_name = 'despesas'

    def _get_filtros(self):
        """Extrai os parâmetros da requisição e garante os valores padrão."""
        get_params = self.request.GET.copy()
        if not get_params.get('data_inicio'):
            get_params['data_inicio'] = date.today().replace(day=1).strftime('%Y-%m-%d')

        return get_params
    
    def get_queryset(self):
        params = self._get_filtros()
        return (
            Despesa.objects.filtrar_por_parametros(params) # Ajuste no seu Custom Manager
            .exclude(forma_pagamento='CARTAO')
            .select_related('grupo', 'especie', 'cartao')
            .order_by('-data')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self._get_filtros()

        data_inicio = params.get('data_inicio')
        data_fim = params.get('data_fim')
        forma_pagamento = params.get('forma_pagamento')
        grupo = params.get('grupo')
        especie = params.get('especie')

        # Total de despesas normais
        total_despesas = self.object_list.aggregate(total=Sum('valor'))['total'] or 0

        # Filtro de parcelas
        parcelas_qs = DespesaParcelaCartao.objects.select_related(
            'despesa', 'despesa__grupo', 'despesa__especie', 'despesa__cartao'
        )

        if forma_pagamento:
            parcelas_qs = parcelas_qs.filter(despesa__forma_pagamento = forma_pagamento)

        if grupo:
            parcelas_qs = parcelas_qs.filter(despesa__grupo_id = grupo)

        if especie:
            parcelas_qs = parcelas_qs.filter(despesa__especie_id = especie)

        if data_inicio:
            parcelas_qs = parcelas_qs.filter(data_vencimento__gte = data_inicio)

        if data_fim:
            parcelas_qs = parcelas_qs.filter(data_vencimento__lte = data_fim)

        total_parcelas = parcelas_qs.aggregate(total=Sum('valor_parcela'))['total'] or 0

        # Avalia o QuerySet em lista uma única vez para enriquecer os dados
        parcelas_processadas = []
        for parcela in parcelas_qs:
            parcela.data = parcela.despesa.data + relativedelta(months = parcela.numero_parcela - 1)
            parcela.descricao = f"{parcela.despesa.descricao} ({parcela.numero_parcela}/{parcela.despesa.parcela})"
            parcela.grupo = parcela.despesa.grupo
            parcela.especie = parcela.despesa.especie
            parcela.forma_pagamento = "CARTAO"
            parcela.valor = parcela.valor_parcela
            parcelas_processadas.append(parcela)

        # Unifica e ordena no Python
        despesas_list = list(self.object_list)
        movimentacoes = sorted(
            chain(despesas_list, parcelas_processadas),
            key=lambda x: getattr(x, 'data', getattr(x, 'data_vencimento', None)),
            reverse=True
        )

        context['movimentacoes'] = movimentacoes
        context['parcelas_cartao'] = parcelas_processadas
        context['total_filtrado'] = total_despesas + total_parcelas

        return context

# ─────────────────────────────────────────────────────────────────────
# Criar Despesa
# ─────────────────────────────────────────────────────────────────────
class DespesaCreateView(CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = "app_despesa/despesacreate.html"
    success_url = reverse_lazy('despesa')

    def form_valid(self, form):
        is_ajax = (
                self.request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest' or
                'application/json' in self.request.headers.get('Accept', '')
            )

        try:
            # Salva os dados no banco de dados
            self.object = form.save() 
            acoes = self.request.POST.getlist('acao')
            acao = acoes[-1] if acoes else None

            if is_ajax:
                return JsonResponse({
                    'status': 'sucesso',
                    'titulo': '✅ Sucesso!',
                    'mensagem': f'Despesa "{self.object.descricao}" lançada com sucesso!',
                    'redirect_url': str(self.success_url),
                    'acao': acao
                    })
            return HttpResponseRedirect(self.get_success_url())

        except IntegrityError as e:
            if is_ajax:
                return JsonResponse({
                    'status': 'erro',
                    'titulo': '❌ Registro Duplicado',
                    'mensagem': 'Esta despesa já foi cadastrada. Verifique os dados informados.'
                }, status = 400)
            raise

        except ValidationError as e:
            if is_ajax:
                 return JsonResponse({
                    'status': 'erro',
                    'titulo': '❌ Erro no Servidor',
                    'mensagem': f'Ocorreu um erro ao salvar: {str(e)}'
                }, status = 500)
            raise


    def form_invalid(self, form):
        # Verifica se é AJAX (case insensitive)
        is_ajax = (
            self.request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest' or
            'application/json' in self.request.headers.get('Accept', '')
        )

        if is_ajax:
            erros_detalhados = []
            for campo, lista_erros in form.errors.items():
                if campo == '__all__':
                    label = 'Verifique'
                else:
                    label = form.fields[campo].label or campo
                
                for erro in lista_erros:
                    erros_detalhados.append(f"• <strong>{label}:</strong> {erro}")

            # Mensagem personalizada para cartão duplicado (se aplicável)
            mensagem_final = '<br>'.join(erros_detalhados)

             # Se houver erro de duplicidade, adiciona dica
            if 'já existe' in mensagem_final.lower() or 'unique' in mensagem_final.lower():
                mensagem_final += '<br><br>💡 Dica: Verifique se esta despesa já foi cadastrada anteriormente.'
            
            return JsonResponse({
                'status': 'erro',
                'titulo': '❌ Erro de validação',
                'mensagem': mensagem_final
            }, status = 400)
        
        return super().form_invalid(form)

# ──────────────────────────────────────────────────────────────────────
# Buscasr espécie
# ──────────────────────────────────────────────────────────────────────
def buscar_especies(request):
    grupo_id = request.GET.get('grupo_id')
    especies = Especie.objects.filter(grupo_id = grupo_id).values('id', 'nomeEspecie')
    return JsonResponse(list(especies), safe = False)


# ──────────────────────────────────────────────────────────────────────
# Despesa - Exclusão
# ──────────────────────────────────────────────────────────────────────
class DespesaDeleteView(DeleteView):
    model = Despesa
    success_url = reverse_lazy('despesa')

    def get(self, request, pk, *args, **kwargs):
        despesa = get_object_or_404(Despesa, pk = pk)
        despesa.delete()

        return redirect('despesa')
    
# ────────────────────────────────────────────────────────────────────────
# Despesa - Editar
# ────────────────────────────────────────────────────────────────────────
class DespesaUpdateView(UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'app_despesa/despesaupdate.html'
    success_url = reverse_lazy('despesa')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        for field_name, field in form.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'

            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select form-select-sm'
                
            else:
                field.widget.attrs['class'] = 'form-control form-control-sm'

        return form

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()       # 1. Salva as alterações principais no model Despesa

            forma_pagamento = form.cleaned_data.get('forma_pagamento')
            num_parcelas = form.cleaned_data.get('parcela') or 1

            # CASO 1: Alterou para DINHEIRO (ou qualquer forma diferente de CARTAO)
            if forma_pagamento != 'CARTAO':
                # Remove todas as parcelas atreladas a esta despesa no banco
                self.object.parcelas_cartao.all().delete()

                # Reseta campos de cartão na despesa principal
                self.object.cartao = None
                self.object.parcela = 1
                self.object.save()

            # CASO 2: Manteve ou alterou para CARTÃO
            else:
                # Remove parcelas antigas para recriar com os novos dados/valores/datas
                self.object.parcelas_cartao.all().delete()

                valor_parcela = self.object.valor / num_parcelas
                data_base = self.object.data

                novas_parcelas = []
                for i in range(1, num_parcelas + 1):
                    # Avança 1 mês para cada parcela (ajuste a regra de vencimento se necessário)
                    vencimento = data_base + relativedelta(months = i - 1)
                    novas_parcelas.append(
                        DespesaParcelaCartao(
                            despesa = self.object,
                            numero_parcela = i,
                            valor_parcela = valor_parcela,
                            data_vencimento = vencimento
                        )
                    )
                # Salva todas as parcelas no banco
                DespesaParcelaCartao.objects.bulk_create(novas_parcelas)

        # Resposta para AJAX (XMLHttpRequest)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'sucesso',
                'titulo': 'Despesa atualizada',
                'mensagem': 'Registro alterado com sucesso.',
                'redirect_url': str(self.success_url)
            })

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
            'status': 'erro',
            'titulo': 'Erro de validação',
            'mensagem': str(form.errors)            
        }, status = 400)

        return super().form_invalid(form)
    
# ───────────────────────────────────────────────────────────────────────────────────────────
# Resumo Despesa
# ───────────────────────────────────────────────────────────────────────────────────────────
class DespesaResumoView(TemplateView):
    template_name = 'app_despesa/despesaresumo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoje = date.today()

        # 1. Tratamento seguro de datas
        try:
            data_inicial_str = self.request.GET.get('data_inicial')
            data_inicial = date.fromisoformat(data_inicial_str) if data_inicial_str else hoje.replace(day = 1)

        except (ValueError, TypeError):
            data_inicial = hoje.replace(day = 1)

        try:
            data_final_str = self.request.GET.get('data_final')
            data_final = date.fromisoformat(data_final_str) if data_final_str else hoje

        except(ValueError, TypeError):
            data_final = hoje

        # Estrutura flexível para acumular totais por grupo e espécie
        # Estrutura: { grupo_nome: { 'total': 0.0, 'subgrupos': { especie_nome: 0.0 } } }
        dados_resumo = defaultdict(lambda: {'total': Decimal('0'), 'subgrupos': defaultdict(lambda: Decimal('0'))})

        # 2. Despesas Normais (À vista / Dinheiro / PIX) agregadas no banco
        despesas_normais = (
            Despesa.objects
            .exclude(forma_pagamento='CARTAO')
            .filter(data__gte = data_inicial, data__lte = data_final)
            .values('grupo__nomeGrupo', 'especie__nomeEspecie')
            .annotate(total_subgrupo=Sum('valor'))
        )

        for item in despesas_normais:
            grupo = item['grupo__nomeGrupo'] or 'Sem Grupo'
            especie = item['especie__nomeEspecie'] or 'Outros'
            valor = item['total_subgrupo'] or 0

            dados_resumo[grupo]['total'] += valor
            dados_resumo[grupo]['subgrupos'][especie] += valor

        # 3. Parcelas de Cartão agregadas DIRETAMENTE no banco
        parcelas_cartao = (
            DespesaParcelaCartao.objects
            .filter(data_vencimento__gte=data_inicial, data_vencimento__lte=data_final)
            .values('despesa__grupo__nomeGrupo', 'despesa__especie__nomeEspecie')
            .annotate(total_subgrupo=Sum('valor_parcela'))
        )

        for item in parcelas_cartao:
            grupo = item['despesa__grupo__nomeGrupo'] or 'Sem Grupo'
            especie = item['despesa__especie__nomeEspecie'] or 'Outros'
            valor = item['total_subgrupo'] or 0

            dados_resumo[grupo]['total'] += valor
            dados_resumo[grupo]['subgrupos'][especie] += valor

        # 4. Formatação final dos dados para envio ao Template
        resumo_grupos = []
        total_geral = 0

        for grupo_nome in sorted(dados_resumo.keys()):
            info_grupo = dados_resumo[grupo_nome]
            total_geral += info_grupo['total']

            subgrupos = [
                {
                    'nome_subgrupo': especie_nome,
                    'valor_subgrupo': valor
                }
                for especie_nome, valor in sorted(info_grupo['subgrupos'].items())
            ]

            resumo_grupos.append({
                'nome_grupo': grupo_nome,
                'total_geral_grupo': info_grupo['total'],
                'subgrupos': subgrupos
            })

            context.update({
                'resumo_grupos': resumo_grupos,
                'total_geral': total_geral,
                'data_inicial': data_inicial.isoformat(),
                'data_final': data_final.isoformat(),
            })

            return context


