"""
Formulários de mídias - NewMedia PWA
"""
from django import forms
from .models import Midia


class MidiaForm(forms.ModelForm):
    """
    Formulário de criação/edição de mídia
    """
    class Meta:
        model = Midia
        fields = ['descricao', 'tipo', 'tags', 'arquivo']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a descrição da mídia',
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: trabalho, pessoal, importante',
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'descricao': 'Descrição',
            'tipo': 'Tipo',
            'tags': 'Tags',
            'arquivo': 'Arquivo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].required = False
        self.fields['arquivo'].required = False
