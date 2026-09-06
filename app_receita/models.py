from django.db          import models
from django.conf        import settings


# ────────────────────────────────────────────────────────────────────────────────
# Receita - Criar
# ────────────────────────────────────────────────────────────────────────────────
class Receita(models.Model):
    CHOICE_CATEGORIA = [
        ('13ºSALARIO', '13º Salário'),
        ('EVENTUAL', 'Eventual'),
        ('FREELANCER', 'Freelancer'),
        ('INVESTIMENTO', 'Investimento'),
        ('OUTROS', 'Outras Receitas'),
        ('RESTITUICAO', 'Restituição de IR'),
        ('SALARIO', 'Salário'),
    ]

    usuario = models.ForeignKey(
       settings.AUTH_USER_MODEL,
       on_delete        = models.CASCADE,
    )
    fonte = models.CharField(
        verbose_name    = 'Fonte Pagadora',
        max_length      = 100,
    )
    descricao = models.CharField(
        verbose_name    = 'Descrição',
        max_length      = 100,
        blank           = True,        
    )
    data_recebimento = models.DateField(
        verbose_name    = 'Data de Recebimento',
    )
    valor = models.DecimalField(
        verbose_name    = 'Valor (R$)',
        max_digits      = 11,
        decimal_places  = 2,
    )
    categoria = models.CharField(
        verbose_name    = 'Categoria',
        max_length      = 50,
        choices         = CHOICE_CATEGORIA,
        default         = 'SALARIO',
    )
    observacao = models.TextField(
        verbose_name    = 'Observação',
        blank           = True,
        default         = '',
    )
    criado_em = models.DateTimeField(
        auto_now_add    = True
    )
    atualizado_em = models.DateTimeField(
        auto_now        = True
    )

    @property
    def nome_titular(self):
        """Extrai apenas o nome da representação do usuário, ignorando o e-mail entre parênteses."""
        if not self.usuario:
            return ""
        
        texto_usuario = str(self.usuario)
        # Se houver parênteses com o e-mail, pega só a parte do nome que vem antes
        if '(' in texto_usuario:
            return texto_usuario.split('(')[0].strip()
            
        return texto_usuario
    
    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        ordering = ['-data_recebimento']
        db_table = "receita"

    def __str__(self):
        data_str = self.data_recebimento.strftime('%d/%m/%Y') if self.data_recebimento else 'Sem data'
        return f"{self.fonte} - R$ {self.valor} ({data_str})"




