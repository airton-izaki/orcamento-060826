from collections                        import defaultdict
from datetime                           import date
from decimal                            import Decimal
from django.shortcuts                   import render
from django.views.generic               import TemplateView, CreateView, ListView, View
from django.urls                        import reverse_lazy
from django.http                        import JsonResponse
from django.db                          import models
from django.db.models                   import Sum, Q




from app_cartao.models                  import CartaoCreate, DespesaParcelaCartao, FaturaCartao
from app_cartao.forms.cartaocreateform  import CartaoCreateForm
from app_cartao.forms.ResumoDespesaForm import ResumoCartaoForm






# ──────────────────────────────────────────────────────────────────────────────
# Cartao
# ──────────────────────────────────────────────────────────────────────────────
class CartaoView(TemplateView):
    template_name = 'app_cartao/cartao.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ResumoCartaoForm(self.request.GET or None)

        # 1. Buscamos as parcelas trazendo os relacionamentos acoplados (INNER JOIN)
        parcelas = DespesaParcelaCartao.objects.select_related(
            'despesa__especie',
            'despesa__cartao'
        ).order_by('-data_vencimento')

        hoje = date.today()       
        ano_atual = hoje.year
        mes_atual = hoje.month

        # Definimos os valores padrão ANTES da validação
        ano_referencia = None
        cartao = None
        status = None
        origem = None
        
        # 2. Aplicamos os filtros básicos e de STATUS direto no banco de dados
        if form.is_valid():
            ano_campo = form.cleaned_data.get('ano')
            ano_referencia = int(ano_campo) if ano_campo else None         
            cartao = form.cleaned_data.get('cartao')
            status = form.cleaned_data.get('status')
            origem = form.cleaned_data.get('origem')
        
        else:
            ano_referencia = ano_atual

        if ano_referencia:
            parcelas = parcelas.filter(data_vencimento__year=ano_referencia)            

        # Filtro de Cartão específico
        if cartao:
            parcelas = parcelas.filter(despesa__cartao = cartao)

        # Filtro Origem
        if origem:
            parcelas = parcelas.filter(despesa__origem = origem)

        # Filtro de Status (Pago / Pendente) executado direto no Banco
        if status == 'PENDENTE':               
            if ano_referencia:
                if ano_referencia == ano_atual:
                    parcelas = parcelas.filter(data_vencimento__month__gte = mes_atual)
                elif ano_referencia < ano_atual:
                    # Se olharmos um ano passado, teoricamente nada é pendente pro futuro
                    parcelas = parcelas.none()
            
            else:
                parcelas = parcelas.filter(
                    (models.Q(data_vencimento__year=ano_atual) & models.Q(data_vencimento__month__gte=mes_atual)) |
                    models.Q(data_vencimento__year__gt=ano_atual)
                )

        elif status == 'PAGO':
            if ano_referencia:
                if ano_referencia == ano_atual:
                    parcelas = parcelas.filter(data_vencimento__month__lt = mes_atual)
                elif ano_referencia > ano_atual:
                    # Se olharmos o futuro, nada foi pago ainda
                    parcelas = parcelas.none()

            else:
                parcelas = parcelas.filter(
                    (models.Q(data_vencimento__year=ano_atual) & models.Q(data_vencimento__month__lt=mes_atual)) |
                    models.Q(data_vencimento__year__lt=ano_atual)
                )

        # dicionários estruturais para a matriz do relatório
        tabela = defaultdict(lambda: defaultdict(Decimal))
        categorias = set()
        competencias = []

        meses_ptbr = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',  5: 'Maio', 6: 'Junho', 
            7: 'Julho', 8: 'Agosto',  9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
        }

        for parcela in parcelas:
            despesa_mae = parcela.despesa
            data = parcela.data_vencimento
           
            # Cria chaves de ordenação (Ex: "2026-01", "2026-02")
            chave_competencia = f'{data.year}-{data.month:02d}'
            competencia_texto = f'{meses_ptbr[data.month]}/{data.year}'

            categoria = despesa_mae.especie.nomeEspecie

            # Alimenta a matriz
            tabela[chave_competencia]['competencia'] = competencia_texto
            tabela[chave_competencia][categoria] += parcela.valor_parcela
            tabela[chave_competencia]['TOTAL'] += parcela.valor_parcela

            tabela[chave_competencia]["ano_num"] = data.year
            tabela[chave_competencia]["mes_num"] = data.month

            tabela[chave_competencia]["cartao_id"] = cartao.id if cartao else None
            categorias.add(categoria)
           
            if chave_competencia not in competencias:
                competencias.append(chave_competencia)

        # Ordenamos as categorias e competências
        categorias_ordenadas = sorted(list(categorias))
        competencias_ordenadas = sorted(competencias)

        # Montamos a estrutura simplificada para o Template
        tabela_processada = []

        for chave in competencias_ordenadas:
            linha_dados = tabela[chave]
            
            # Cria a lista de valores alinhada exatamente com a ordem das categorias
            valores_categoria = [
                linha_dados.get(cat, None) for cat in categorias_ordenadas
            ]

            tabela_processada.append({
                'competencia': linha_dados['competencia'],
                'valores': valores_categoria,
                'total': linha_dados['TOTAL'],
                'ano_num': linha_dados['ano_num'],
                'mes_num': linha_dados['mes_num'],
            })

        # Envia os dados perfeitamente estruturados e ordenados para o template
        context['tabela_processada'] = tabela_processada
        context['categorias'] = categorias_ordenadas
        context['form'] = form

        return context

# ──────────────────────────────────────────────────────────────────────────────
# Criar
# ──────────────────────────────────────────────────────────────────────────────
class CartaoCreateView(CreateView):
    model = CartaoCreate
    form_class = CartaoCreateForm
    template_name = 'app_cartao/cartaocreate.html'
    success_url = reverse_lazy('cartao')

    def form_valid(self, form):
        self.object = form.save()
        
        # Verifica se espera JSON
        if 'application/json' in self.request.headers.get('Accept', ''):
            return JsonResponse({
                'status': 'sucesso',
                'titulo': 'Cartão cadastrado!',
                'mensagem': f'Cartão {self.object.nome_cartao} - Final {self.object.final} foi criado com sucesso!',  # <-- Usando nome_cartao
                'redirect_url': str(self.success_url)
            })
        
        return super().form_valid(form)

    def form_invalid(self, form):
        if 'application/json' in self.request.headers.get('Accept', ''):
            erros = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        erros.append(f'⚠️ {error}')
                    
                    else:
                        field_label = form.fields[field].label or field
                        erros.append(f'• {field_label}: {error}')
            
            return JsonResponse({
                'status': 'erro',
                'titulo': 'Erro de validação',
                'mensagem': '<br>'.join(erros) if erros else 'Verifique os dados informados.'
            }, status=400)
        
        return super().form_invalid(form)

# ────────────────────────────────────────────────────────────────────────
# Listar Cartão
# ──────────────────────────────v─────────────────────────────────────────
class CartaoListarView(ListView):
    model = CartaoCreate
    template_name = 'app_cartao/cartaolistar.html'
    context_object_name = 'cartoes'

# ─────────────────────────────────────────────────────────────────────────
# Fatura do Cartão
# ─────────────────────────────────────────────────────────────────────────
class CartaoFaturaView(TemplateView):
    template_name = 'app_cartao/fatura.html'

    def get(self, request):
      
        cartao_id = request.GET.get('cartao_id')
        ano = request.GET.get('ano')
        mes = request.GET.get('mes')

        if not all([cartao_id, ano, mes]):
            return render(
                 request,
                self.template_name,
                {}
            )    
          
        cartao = CartaoCreate.objects.get(pk=cartao_id)
        parcelas = DespesaParcelaCartao.objects.filter(
            despesa__cartao = cartao,
            data_vencimento__year = ano,
            data_vencimento__month = mes,
        )

        valor_total_fatura = ( parcelas.aggregate( total = Sum('valor_parcela'))['total']
            or Decimal('0.00')
        )

        compras_nacionais = valor_total_fatura
        compras_internacionais = Decimal('0.00')
        
        valor_minimo = valor_total_fatura * Decimal('0.75')

        fatura_atual, created = FaturaCartao.objects.get_or_create(
            cartao = cartao,
            ano = ano,
            mes = mes
        )

        saldo_remanescente = (
            Decimal(valor_total_fatura) +  Decimal(fatura_atual.total_encargos) -  Decimal(fatura_atual.valor_pago)
        )

        context = {
            'cartao': cartao,
            'cartao_selecionado': cartao.id,
            'ano_selecionado': int(ano),
            'mes_selecionado': int(mes),

            'mes_nome': fatura_atual.get_mes_display(),
            
            'valor_total_fatura': valor_total_fatura,
            'compras_nacionais': compras_nacionais,
            'compras_internacionais': compras_internacionais,
            'valor_minimo': valor_minimo,

            'fatura_atual': fatura_atual,
            'saldo_remanescente': saldo_remanescente,                    
        }
     
        return render ( request,  self.template_name,   context )

# ───────────────────────────────────────────────────────────────────────────────────────
# Selecionar Fatura
# ───────────────────────────────────────────────────────────────────────────────────────
class SelecionarFaturaView(View):
    template_name = 'app_cartao/selecionarfatura.html'

    def get(self, request):
        cartoes = CartaoCreate.objects.all().order_by('nome_cartao')

        context = {
            'cartoes': cartoes
        }

        return render(
            request,
            self.template_name,
            context
        )





