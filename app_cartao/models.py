from django.db import models
from django.core.validators     import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions     import ValidationError
from django.db.models           import Sum
from decimal                    import Decimal
from datetime                   import date



# ──────────────────────────────────────────────────────────────────────────────
# Create
# ──────────────────────────────────────────────────────────────────────────────
class CartaoCreate(models.Model):
    CHOICE_STATUS_CARTAO = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
    ]

    CHOICE_BANDEIRA_CARTAO = [
        ('MASTERCARD', 'Mastercard'), 
        ('VISA', 'Visa'),  
        ('ELO', 'Elo'),
    ]

    CHOICE_TIPO_CARTAO = [
        ('TITULAR', 'Titular'), 
        ('DEPENDENTE', 'Dependente'),
        ('ESTUDANTE', 'Estudante'),
    ]

    cartao_principal = models.ForeignKey(
        'self',
        verbose_name = 'Titular (se for dependente)',
        on_delete    = models.CASCADE,
        null         = True,
        blank        = True,
        related_name = 'dependentes',
    )

    titular = models.CharField(
        verbose_name = 'Nome impresso no cartão',
        max_length   = 100,
        blank        = False,
        null         = False,
    )

    banco = models.CharField(
        verbose_name  = 'Banco Emissor',
         max_length   = 50,
         blank        = False,
         null         = False,
    )

    nome_cartao = models.CharField(
        verbose_name = 'Nome do cartão',
        max_length   = 100,
        blank        = False,
        null         = False,
    )

    bandeira = models.CharField(
        verbose_name = 'Bandeira',
        max_length   = 50,
        choices      = CHOICE_BANDEIRA_CARTAO
    )

    categoria = models.CharField(
        verbose_name = 'Categoria (Ex: Nanquim, Black)',
        max_length   = 50,
        blank        = True,
        null         = True,
    )

    final = models.CharField(
        verbose_name = 'Final do cartão',
        max_length   = 4,
        validators   = [RegexValidator(r'^\d{4}$', 'Digite exatamente 4 dígitos numéricos')],
    )

    limite = models.DecimalField(
        verbose_name = 'Limite de Compra',
        max_digits   = 10,
        decimal_places = 2
    )

    dia_vencimento = models.PositiveIntegerField(
        verbose_name = 'Dia de Vencimento',
        validators   = [
            MinValueValidator(1, 'Dia deve ser entre 1 e 31'),
            MaxValueValidator(31, 'Dia deve ser entre 1 e 31')
        ],
    )

    dia_limite = models.PositiveIntegerField(
        verbose_name = 'Dia de Fechamento (Melhor dia de compra)',
        validators   = [
            MinValueValidator(1, 'Dia deve ser entre 1 e 31'),
            MaxValueValidator(31, 'Dia deve ser entre 1 e 31')
        ],
    )

    status = models.CharField(
        verbose_name = 'Status',
        max_length   = 10,
        choices      = CHOICE_STATUS_CARTAO,
        default      = 'ATIVO',
    )

    tipo_cartao = models.CharField(
        verbose_name = 'Tipo de cartão',
        max_length   = 20,
        choices      = CHOICE_TIPO_CARTAO,
        default      = 'TITULAR',
    )

    virtual = models.BooleanField(
        verbose_name = 'Cartão Virtual',
        default      = False,
        help_text    = 'Marque sim se for cartão virtual',
    )

    observacao = models.TextField(
        verbose_name = 'Observações',
        blank        = True,
        null         = True
    )

    criado_em = models.DateField(
        verbose_name = 'Data da criação',
        auto_now_add = True
    )

    atualizado_em = models.DateField(
        verbose_name = 'Última atualização',
        auto_now     = True,
    )

    class Meta:
        verbose_name        = 'Cartão'
        verbose_name_plural = 'Cartões'
        ordering            = ['nome_cartao']
        db_table            = 'cartao'
        constraints         = [
            models.UniqueConstraint(
                fields = ['banco', 'bandeira', 'final'],
                name   = 'unique_cartao_fisico'
            )
        ]

    def __str__(self):
         return f'{self.nome_cartao} - {self.final}'


# ────────────────────────────────────────────────────────────────────────
# Paarcelas do cartão
# ────────────────────────────────────────────────────────────────────────
class DespesaParcelaCartao(models.Model):
    despesa = models.ForeignKey(
        'app_despesa.Despesa',
        verbose_name    = 'Despesa',
        on_delete       = models.CASCADE,
        related_name    = 'parcelas_cartao'
    )

    numero_parcela = models.PositiveIntegerField(
        verbose_name   ='Número da Parcela'
    )

    valor_parcela = models.DecimalField(
        verbose_name   = 'Valor da Parcela',
        max_digits     = 12,
        decimal_places = 2,
    )

    data_vencimento = models.DateField(
        verbose_name   = 'Data de Vencimento'
    )

    criado_em = models.DateTimeField(
        verbose_name   = 'Criado em',
        auto_now_add   = True
    )

    atualizado_em = models.DateTimeField(
        verbose_name  = 'Atualizado em',
        auto_now      = True
    )

    class Meta:
        verbose_name        = 'Parcela do Cartão'
        verbose_name_plural = 'Parcelas do Cartão'
        db_table            = 'despesa_parcela_cartao'
        ordering            = ['data_vencimento']

    def __str__(self):
        return (
             f'{self.despesa.descricao} - '
             f'{self.numero_parcela}/{self.despesa.parcela}'
        )

    @property
    def mes_referencia(self):
        return self.data_vencimento.strftime('%m/%Y')


    @property
    def descricao_resumida(self):
        return (
            f'{self.numero_parcela}/{self.despesa.parcela} '
            f'- R$ {self.valor_parcela:.2f}'
        )

    @property
    def status(self):
        hoje = date.today()

        # 1. Se o ano do vencimento for menor que o ano atual, o mês com certeza já passou.
        if self.data_vencimento.year < hoje.year:
            return 'PAGO'

        elif self.data_vencimento.year > hoje.year:
             return 'PENDENTE'

        else:
            if self.data_vencimento.month < hoje.month:
                 return 'PAGO'

            else:
                return 'PENDENTE'

    @property
    def is_pendente(self):
        return self.status == 'PENDENTE'

# ────────────────────────────────────────────────────────────────────────
# Faturas do cartão
# ────────────────────────────────────────────────────────────────────────
class FaturaCartao(models.Model):
    CHOICE_MESES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]

    cartao = models.ForeignKey(
        CartaoCreate, 
        on_delete    = models.CASCADE, 
        related_name = 'faturas',
    )
    ano = models.PositiveIntegerField(
        verbose_name = 'Ano',
        validators   = [
            MinValueValidator(2000),
            MaxValueValidator(2100),
        ],
    )
    mes = models.PositiveIntegerField(
        verbose_name = 'Mês',
        choices      = CHOICE_MESES
    )
    data_fechamento = models.DateField(
        verbose_name = "Data de Fechamento", 
        null = True, 
        blank = True
    )
    data_vencimento = models.DateField(
        verbose_name = "Data de Vencimento", 
        null = True, 
        blank = True
    )
    total_encargos = models.DecimalField(
        verbose_name   = 'Encargos',
        max_digits     = 10, 
        decimal_places = 2, 
        default        = Decimal('0.00'),
    )
    valor_pago = models.DecimalField(
        verbose_name    = 'Valor Pago',
        max_digits      = 10, 
        decimal_places  = 2, 
        default         = Decimal('0.00'),
    )

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        unique_together = ('cartao', 'ano', 'mes')
        db_table =  'fatura'
        constraints = [
            models.UniqueConstraint(
                fields = ["cartao", "ano", "mes"],
                name = "unique_fatura_por_cartao_ano_mes",
            )
        ]

    def __str__(self):
        return f"Fatura {self.cartao.nome_cartao} - {self.get_mes_display()}/{self.ano}"























