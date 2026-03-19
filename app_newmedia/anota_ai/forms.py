from django import forms
from .models import Anotacao

class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = Anotacao
        fields = ['titulo', 'tipo', 'texto', 'pix_nome', 'pix_chave', 'pix_favorecido', 'pix_banco']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da anotação'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pix_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identificação do PIX'}),
            'pix_chave': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chave PIX'}),
            'pix_favorecido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Favorecido'}),
            'pix_banco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instituição Bancária'}),
        }
