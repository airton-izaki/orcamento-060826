from django             import forms
from app_despesa.models import Despesa, Especie


class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = [
            'grupo', 'especie', 'descricao', 'cartao', 'local', 'data', 
            'forma_pagamento', 'origem', 'parcela', 'valor', 'observacao'
        ]

        widgets = {
            'grupo': forms.Select( attrs = {
                'class':    'form-select',
                'id': 'id_grupo',
            }),
        
            'especie': forms.Select( attrs = {
                'class':    'form-select', 
                'id': 'id_especie',   
            }),

            'descricao': forms.TextInput( attrs = {
                'class':    'form-control',
                'placeholder': 'Descrição do produto',
            }),

            'cartao': forms.Select( attrs = {
                'class': 'form-select', 
                'id': 'id_cartao',
            }),

            'local': forms.TextInput( attrs = {
                'class':    'form-control',
                'placeholder': 'Local da compra',
            }),

            'data': forms.DateInput( attrs = {
                'type': 'date', 
                'class': 'form-control',
            }),

            'forma_pagamento': forms.Select( attrs = {
                'class': 'form-select', 
                'id': 'id_forma_pagamento'
            }),

            'origem': forms.Select( attrs = {
                'class': 'form-select',
                'id': 'id_origem'
            }),

            'parcela': forms.NumberInput( attrs = {
                'class': 'form-control', 
                'id': 'id_parcela', 
                'min': 1
            }),

            'valor': forms.NumberInput( attrs = {
                'class': 'form-control', 
                'step': '0.01'
            }),

            'observacao': forms.Textarea( attrs = {
                'class':    'form-control',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Torna os campos não-obrigatórios na validação base do formulário
        self.fields['parcela'].required = False
        self.fields['cartao'].required = False

        self.fields['especie'].queryset = Especie.objects.none()

        if 'grupo' in self.data:
            try:
                grupo_id = int(self.data.get('grupo'))
                self.fields['especie'].queryset = Especie.objects.filter(
                    grupo_id = grupo_id
                )

            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields['especie'].queryset = Especie.objects.filter(
                grupo = self.instance.grupo
            )

    def clean(self):
        cleaned_data = super().clean()
        forma_pagamento = cleaned_data.get('forma_pagamento')
        cartao = cleaned_data.get('cartao')
        parcela = cleaned_data.get('parcela')

        if forma_pagamento == 'CARTAO':
            # Se for EDIÇÃO e o cartão veio vazio no POST, recupera o cartão salvo anteriormente
            if not cartao and self.instance and self.instance.pk:
                cartao = self.instance.cartao
                cleaned_data['cartao'] = cartao

            # Se for EDIÇÃO e a parcela veio vazia no POST, recupera a parcela salva anteriormente
            if not parcela and self.instance and self.instance.pk:
                parcela = self.instance.parcela
                cleaned_data['parcela'] = parcela

            # Se mesmo após recuperar (ou em criação) continuar vazio, lança os erros
            if not cartao:
                self.add_error('cartao', 'Selecione o cartão de crédito utilizado.')

            if not parcela:
                self.add_error('parcela', 'A quantidade de parcelas deve ser maior ou igual a 1.')
                
        else:
            cleaned_data['cartao'] = None

        return cleaned_data
