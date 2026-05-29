from django import forms
from .models import NotificacaoCompra

class NotificacaoCompraForm(forms.ModelForm):
    class Meta:
        model = NotificacaoCompra
        fields = [
            'estabelecimento', 
            'valor', 
            'data_compra', 
            'hora_compra', 
            'tipo_transacao', 
            'cartao_final', 
            'texto_completo'
        ]
        widgets = {
            'data_compra': forms.DateInput(attrs={'type': 'date'}),
            'hora_compra': forms.TimeInput(attrs={'type': 'time'}),
            'texto_completo': forms.Textarea(attrs={'rows': 3}),
        }
