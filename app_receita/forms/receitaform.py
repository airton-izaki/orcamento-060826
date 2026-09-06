from django import forms
from app_receita.models import Receita

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = '__all__'
        widgets = {
            'usuario': forms.Select( attrs = {
                'class': 'form-select'
            }),
            'fonte': forms.TextInput( attrs = {
                'class': 'form-control', 
                'placeholder': 'Ex: Empresa X'
            }),
            'descricao': forms.TextInput( attrs = {
                'class': 'form-control', 
                'placeholder': 'Ex: Pagamento referente ao projeto Y'
            }),
            'data_recebimento': forms.DateInput(
                format = '%Y-%m-%d',
                attrs = {'type': 'date', 'class': 'form-control'}
            ),
            'valor': forms.NumberInput( attrs = {
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': '0.00'
            }),
            'categoria': forms.Select( attrs = {
                'class': 'form-select'
            }),
            'observacao': forms.Textarea(attrs = {
                'class': 'form-control',
                'rows': 3
            }),
        }