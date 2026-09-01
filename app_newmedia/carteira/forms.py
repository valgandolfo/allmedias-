from django import forms
from .models import NotificacaoCompra, BancoMonitorado

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
        }


class BancoMonitoradoForm(forms.ModelForm):
    class Meta:
        model = BancoMonitorado
        fields = ['nome', 'pacote_android', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nubank'}),
            'pacote_android': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: com.nu.production'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
