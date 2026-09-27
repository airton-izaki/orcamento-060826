from django import forms
from app_investimento.models        import InvestimentoCreate

class InvestimentoCreateForm(forms.ModelForm):
    class Meta:
        model = InvestimentoCreate
        fields = [
            'nome_investimento',
            'tipo',
            'instituicao',
            'data_aplicacao',
            'data_vencimento',
            'valor_inicial',            
            'observacao',
            'ativo',
        ]
    
        widgets = {
            'nome_investimento': forms.TextInput( attrs = {
                'class': 'form-control'
            }),
            'tipo': forms.Select( attrs = {
                'class': 'form-select'
            }),
            'instituicao': forms.TextInput( attrs = {
                'class': 'form-control'
            }),
            'data_aplicacao': forms.DateInput( attrs = {
                'class': 'form-control',
                'type': 'date'
            }),
            'data_vencimento': forms.DateInput( attrs = {
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_inicial': forms.NumberInput( attrs = {
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0,00'
            }),           
            'observacao': forms.Textarea( attrs = {
                'class': 'form-control',
                'rows': 3
            }),
            'ativo': forms.CheckboxInput( attrs = {
                'class': 'form-check-input'
            }),
        }