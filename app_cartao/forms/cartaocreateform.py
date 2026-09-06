from django             import forms
from app_cartao.models  import CartaoCreate


class CartaoCreateForm(forms.ModelForm):
    class Meta:
        model = CartaoCreate
        fields = [
            'cartao_principal', 'titular', 'banco', 'nome_cartao', 'bandeira', 'categoria',
            'final', 'limite', 'dia_vencimento', 'dia_limite', 'status', 'tipo_cartao', 'virtual',
            'observacao'
        ]

        widgets = {
            'cartao_principal':  forms.Select( attrs = {
                'class': 'form-select',
            }), 
            'titular': forms.TextInput( attrs = {
                'class': 'form-control',
                'placeholder': 'Nome'
            }), 
            'banco': forms.TextInput( attrs = {
                'class': 'form-control',
                'placeholder': 'Banco emissor',
            }), 
            'nome_cartao':  forms.TextInput( attrs = {
                'class': 'form-control',
                'placeholder': 'Nome do cartão',
            }), 
            'bandeira':  forms.Select( attrs = {
                'class': 'form-select'
            }), 
            'categoria': forms.TextInput( attrs = {
                'class': 'form-control',
                'placeholder': 'Ex.: Gold, Platinum, Black'
            }),
            'final':  forms.TextInput( attrs = {
                'class': 'form-control',
                'help_texts': '4 últimos dígitos',
                'maxlength': '4',
            }), 
            'limite':  forms.NumberInput( attrs = {
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }), 
            'dia_vencimento':  forms.NumberInput( attrs = {
                'class': 'form-control',
                'min': 1,
                'max': 31,    
                'placeholder': 'Dia do Vencimento',            
            }), 
            'dia_limite':  forms.NumberInput( attrs = {
                'class': 'form-control',
                'min': 1,
                'max': 31,
                'placeholder': 'Melhor dia de compra',
            }), 
            'status':  forms.Select( attrs = {
                'class': 'form-select'
            }), 
            'tipo_cartao':  forms.Select( attrs = {
                'class': 'form-select'
            }), 
            'virtual':  forms.CheckboxInput( attrs = {
                'class': 'form-check-input'
            }),
            'observacao':  forms.Textarea( attrs = {
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observação',
            }),
        }

        help_texts = {
            'final': 'Digite os 4 últimos números',
            'dia_vencimento': 'Dia da fatura',
            'dia_limite': 'Melhor dia de compra'
        }

        labels = {
            'cartao_principal':  'Cartão Principal',
            'titular':  'Nome Impresso no Cartão', 
            'banco':  'Banco Emissor', 
            'nome_cartao':  'Nome do Cartão', 
            'bandeira':  'Bandeira', 
            'categoria':  'Categoria',
            'final':  'Final do Cartão', 
            'limite':  'Limite de Compra', 
            'dia_vencimento':  'Dia de Vencimento', 
            'dia_limite':  'Dia limite', 
            'status':  'Status', 
            'tipo_cartao':  'Tipo de cartão', 
            'virtual':  'É Cartão Virtual?',
            'observacao':  'Observação',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cartao_principal'].queryset = CartaoCreate.objects.filter(
            tipo_cartao='TITULAR'
        )