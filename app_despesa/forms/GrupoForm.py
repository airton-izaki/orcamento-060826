from django             import forms
from app_despesa.models import Grupo

class DespesaGrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = [
            'nomeGrupo'
        ]

        widgets = {
            'nomeGrupo': forms.TextInput( attrs = {
                'class': 'form-control'
            })
        }