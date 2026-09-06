from django             import forms
from app_cartao.models  import CartaoCreate


class ResumoCartaoForm(forms.Form):

    ano = forms.IntegerField(
        label = 'Ano',
        required = False,
        widget = forms.NumberInput( attrs = {
            'class': 'form-control',
            'placeholder': 'Todos os anos (Deixe em branco)'
        })
    )

    cartao = forms.ModelChoiceField(
        label='Cartão',
        queryset = CartaoCreate.objects.filter(status='ATIVO'),
        required=False,
        empty_label='Todos os cartões',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            })
    )

    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[
            ('', 'Todos'),
            ('PAGO', 'Pago'),
            ('PENDENTE', 'Pendente'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            })
    )