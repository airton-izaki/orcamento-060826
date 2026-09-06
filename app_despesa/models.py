from datetime                   import date
from decimal                    import Decimal, ROUND_HALF_UP
from dateutil.relativedelta     import relativedelta
from django.db                  import models
from django.core.exceptions     import ValidationError
from django.db.models           import Sum
from app_cartao.models          import DespesaParcelaCartao


# ────────────────────────────────────────────────────────────────────
# Grupo de despesa - Agrupa as despesas
# ────────────────────────────────────────────────────────────────────
class Grupo(models.Model):
    nomeGrupo = models.CharField(
        verbose_name = 'Grupo de Despesa',
        max_length   = 50,
        unique       = True,       
    )

    class Meta:
        verbose_name = 'Grupo de Despesa'
        verbose_name_plural = 'Grupos de Despesas'
        ordering = ['nomeGrupo']
        db_table = 'grupo'

    def clean(self):
        # Higieniza o dado: remove espaços extras e padroniza (Ex: "  Alimentação  " -> "Alimentação")
        if self.nomeGrupo:
            nome_limpo = self.nomeGrupo.strip().title()           

        # Consulta o banco com o nome já limpo e formatado
        existe = (Grupo.objects.filter(nomeGrupo__iexact = nome_limpo)
            .exclude(pk = self.pk)
            .exists()
        )

        if existe:
            raise ValidationError({
                'nomeGrupo': 'Já existe um grupo com esse nome.'
            })

    def save(self, *args, **kwargs):
        if self.nomeGrupo:
            self.nomeGrupo = self.nomeGrupo.strip().title()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nomeGrupo}"

# ────────────────────────────────────────────────────────────────────
# Espécie de despesa 
# ────────────────────────────────────────────────────────────────────
class Especie(models.Model):
    grupo = models.ForeignKey(
        'Grupo',
        verbose_name  ='Grupo de Despesa',
        on_delete     = models.RESTRICT,
        db_constraint = True,
        null          = False,
        related_name  = "especies",
    )
    nomeEspecie = models.CharField(
        verbose_name = 'Espécie',
        max_length   = 50,
        unique       = True,
        blank        = False,
        null         = False,
    )

    class Meta:
        verbose_name = 'Espécie de Despesa'
        verbose_name_plural = 'Espécies de Despesas'
        ordering = ['nomeEspecie']
        db_table = 'especie'

    def clean(self):
        if self.nomeEspecie:
            nome_limpo = self.nomeEspecie.strip().title()
            existe = (Especie.objects.filter( nomeEspecie__iexact = nome_limpo )
                .exclude( pk = self.pk )
                .exists()
            )

        if existe:
            raise ValidationError({
                'nomeEspecie': 'Já existe uma espécie com esse nome.'
            })

    def save(self, *args, **kwargs ):
        if self.nomeEspecie:
            self.nomeEspecie = self.nomeEspecie.strip().title()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nomeEspecie

# ───────────────────────────────────────────────────────────────────
# Despesa - Criar
# ───────────────────────────────────────────────────────────────────
class DespesaQuerySet(models.QuerySet):
    def do_mes_atual(self):       
        hoje = date.today()
        return self.exclude(forma_pagamento='CARTAO').filter(
            data__year=hoje.year, 
            data__month=hoje.month
        )
        
    def do_mes_atual_cartao(self):
        hoje = date.today()
        # Importação local se necessário para evitar imports circulares
        from .models import DespesaParcelaCartao
        return DespesaParcelaCartao.objects.filter(
            data_vencimento__year=hoje.year, 
            data_vencimento__month=hoje.month
        )
        
    def total(self):
        hoje = date.today()
        from .models import DespesaParcelaCartao

        total_normal = self.exclude(forma_pagamento='CARTAO').filter(
            data__year=hoje.year,
            data__month=hoje.month
        ).aggregate(total=Sum('valor'))['total'] or 0

        total_cartao = DespesaParcelaCartao.objects.filter(
            data_vencimento__year=hoje.year,
            data_vencimento__month=hoje.month,
            despesa__in=self.filter(forma_pagamento='CARTAO')
        ).aggregate(total=Sum('valor_parcela'))['total'] or 0

        return total_normal + total_cartao
        
    def get_nome_mes_atual(self):
        meses_pt_br = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
            7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return meses_pt_br[date.today().month]
        
    def total_cartao(self):
        hoje = date.today()
        from .models import DespesaParcelaCartao

        soma_parcela = DespesaParcelaCartao.objects.filter(
            data_vencimento__year=hoje.year,
            data_vencimento__month=hoje.month
        ).aggregate(total_soma=Sum('valor_parcela'))['total_soma'] or 0

        return soma_parcela
    
    def gerar_resumo_agrupado(self):
        dados_agrupados = self.exclude(forma_pagamento='CARTAO').filter(
            data__year=date.today().year,
            data__month=date.today().month
        ).values(
            'especie__grupo__nomeGrupo',
            'especie__nomeEspecie'
        ).annotate(
            total_especie=Sum('valor')
        ).order_by('especie__grupo__nomeGrupo')

        grupos_dict = {}
        for item in dados_agrupados:
            nome_grupo = item['especie__grupo__nomeGrupo']
            nome_especie = item['especie__nomeEspecie']
            total_especie = item['total_especie']

            if nome_grupo not in grupos_dict:
                grupos_dict[nome_grupo] = {
                    'nome_grupo': nome_grupo,
                    'total_geral_grupo': 0,
                    'subgrupos': []
                }

            grupos_dict[nome_grupo]['total_geral_grupo'] += total_especie
            grupos_dict[nome_grupo]['subgrupos'].append({
                'nome_subgrupo': nome_especie,
                'valor_subgrupo': total_especie
            })
        return list(grupos_dict.values())
        
    def filtrar_por_parametros(self, params):
        qs = self

        # CORREÇÃO: Aceita tanto request.GET quanto dicionários diretos
        get_val = params.get if isinstance(params, dict) else params.GET.get

        data_inicio = get_val('data_inicio') or None
        data_fim = get_val('data_fim') or None
        grupo = get_val('grupo') or None
        especie = get_val('especie') or None
        forma_pagamento = get_val('forma_pagamento') or None

        if forma_pagamento != 'CARTAO':
            if data_inicio and data_fim:
                qs = qs.filter(data__range=[data_inicio, data_fim])
            elif data_inicio:
                qs = qs.filter(data__gte=data_inicio)
            elif data_fim:
                qs = qs.filter(data__lte=data_fim)

        if grupo:
            qs = qs.filter(grupo_id=grupo)
            
        if especie:
            qs = qs.filter(especie_id=especie)            

        if forma_pagamento:
            qs = qs.filter(forma_pagamento=forma_pagamento)

        return qs


class DespesaManager(models.Manager):
    def get_queryset(self):
        return DespesaQuerySet(self.model, using=self._db)

    def do_mes_atual(self):
        return self.get_queryset().do_mes_atual()

    def do_mes_atual_cartao(self):
        return self.get_queryset().do_mes_atual_cartao()

    def total(self):
        return self.get_queryset().total()

    def total_cartao(self):
        return self.get_queryset().total_cartao()

    def gerar_resumo_agrupado(self):
        return self.get_queryset().gerar_resumo_agrupado()

    def filtrar_por_parametros(self, params):
        return self.get_queryset().filtrar_por_parametros(params)

class Despesa(models.Model):
    objects = DespesaManager()

    CHOICE_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('DEBITO', 'Débito em Conta'),
        ('CARTAO', 'Cartão de Crédito')
    ]

    CHOICE_ORIGEM = [
        ('NACIONAL', 'Nacional'),
        ('INTERNACIONAL', 'Internacional'),
    ]
    
    grupo = models.ForeignKey(
        'Grupo',
        verbose_name    = "Grupo de Despesa",
        on_delete       = models.RESTRICT,
        db_constraint   = True,
        null            = False,
        related_name    = 'despesa_gupo',
    )

    especie = models.ForeignKey(
        'Especie',
        verbose_name  = 'Espécie',
        on_delete     = models.RESTRICT,
        db_constraint = True,
        null          = False,
        related_name  = "despesas_especie",
    )

    cartao = models.ForeignKey(
        'app_cartao.CartaoCreate',
        verbose_name  = 'Cartao',
        on_delete     = models.SET_NULL,
        null          = True,
        blank         = True,
    )

    descricao = models.CharField(
        verbose_name  = 'Descrição',
        max_length    = 100,
        blank         = False,
        null          = False,
    )

    local = models.CharField(
        verbose_name  = 'Local',
        max_length    = 100,
        blank         = True,       
    )

    data = models.DateField(
        verbose_name = 'Data',
        blank        = False,
        null         = False,
    )

    forma_pagamento = models.CharField(
        verbose_name = 'Forma de Pagamento',
        max_length   =  50,
        choices      = CHOICE_PAGAMENTO,
        default      = 'DINHEIRO',
    )

    origem = models.CharField(
        verbose_name = 'Origem da Compra',
        max_length   = 15,
        choices      = CHOICE_ORIGEM,
        default      = 'NACIONAL',
    )

    parcela = models.PositiveIntegerField(
        verbose_name = 'Número de Parcelas',
        default      = 1, 
    )

    valor = models.DecimalField(
        verbose_name   = 'Valor',
        max_digits     = 12,
        decimal_places = 2,
    )
    observacao = models.TextField(
        blank = True,
        null  = True
    )
    
    class Meta:
        verbose_name        = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering            = ['-data']
        db_table            = 'despesa'

    def __str__(self):
        return f"{self.descricao}"

    @property
    def descricao_parcelamento(self):
        if self.parcela and self.parcela > 1:
            valor_parcela = self.valor / Decimal(self.parcela)
            return f"{self.parcela}x de R$ {valor_parcela:.2f}"

        return "À vista"   

    def clean(self):
        if self.forma_pagamento == 'CARTAO' and not self.cartao:
            raise ValidationError({'cartao': 'Você deve selecionar um cartão para a forma de pagamento Cartão de Crédito.'})

        if self.forma_pagamento == 'CARTAO' and (not self.parcela or self.parcela < 1):
            raise ValidationError({'parcela': 'O número de parcelas deve ser pelo menos 1 para compras no cartão.'})

    # Salva a despesa principal primeiro
    def save(self, *args, **kwargs):
        self.full_clean()

        is_new = self.pk is None

        super().save(*args, **kwargs)


        if is_new and self.forma_pagamento == 'CARTAO':

            valor_base = self.valor / Decimal(self.parcela)

            valor_duas_casas = valor_base.quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )

            diferenca_centavos = (
                self.valor -
                (valor_duas_casas * self.parcela)
            )


            for i in range(1, self.parcela + 1):

                data_parcela = (
                    self.data +
                    relativedelta(months=i-1)
                )


                valor_final_parcela = valor_duas_casas


                if i == self.parcela:
                    valor_final_parcela += diferenca_centavos


                DespesaParcelaCartao.objects.create(
                    despesa=self,
                    numero_parcela=i,
                    valor_parcela=valor_final_parcela,
                    data_vencimento=data_parcela
                )














