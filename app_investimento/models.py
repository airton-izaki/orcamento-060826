from django.db import models

class InvestimentoCreate(models.Model):
    TIPO_CHOICES = [
        ('CDB', 'CDB'),
        ('POUPANCA', 'Poupança'),
        ('PREVIDENCIA', 'Previdência Privada'),
        ('TESOURO', 'Tesouro Direto'),
        ('ACOES', 'Ações'),
        ('FII', 'Fundos Imobiliários'),
    ]

    nome_investimento = models.CharField(
        verbose_name = 'Nome do Investimento',
        max_length   = 100,
        unique       = True,
    )
    tipo = models.CharField(
        verbose_name = 'Tipo',
        max_length   = 20,
        choices      = TIPO_CHOICES,
    )
    instituicao = models.CharField(
        verbose_name = 'Instituição Financeira',
        max_length   = 100,
    )
    data_aplicacao = models.DateField(
        verbose_name = 'Data da Aplicação',
    )
    data_vencimento = models.DateField(
        verbose_name = 'Data do Vencimento',
        blank        = True,
        null         = True,
    )
    valor_inicial = models.DecimalField(
        verbose_name = 'Valor Inicial',
        max_digits   = 11,
        decimal_places = 2,
    )
    saldo_atual = models.DecimalField(
        verbose_name    = 'Saldo Atual',
        max_digits      = 11,
        decimal_places  = 2,
        blank           = True,
        null            = True,
    )
    observacao = models.TextField(
        verbose_name    = 'Observação',
        blank           = True,
        default         = '',
    )
    ativo = models.BooleanField(
        verbose_name    = 'Ativo',
        default         = True,
    )
    criado_em = models.DateTimeField(
        auto_now_add    = True,
    )
    atualizado_em = models.DateTimeField(
        auto_now        = True,
    )

    class Meta:
        verbose_name = 'Investimento'
        verbose_name_plural = 'Investimentos'
        ordering = ['nome_investimento']
        db_table = 'investimento'

    def __str__(self):
        return self.nome_investimento

    def save(self, *args, **kwargs):
        if not self.pk:
            self.saldo_atual = self.valor_inicial

        super().save(*args, **kwargs)



