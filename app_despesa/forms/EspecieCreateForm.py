from django                 import forms
from app_despesa.models     import Especie


class EspecieCreateForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = [ 'grupo', 'nomeEspecie' ]

        widgets = {
            'grupo': forms.Select( attrs = {
                'class':    'form-select'
            }),
            'nomeEspecie': forms.TextInput( attrs = {
                'class':    'form-control'
            })
        }






