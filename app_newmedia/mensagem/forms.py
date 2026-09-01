from django import forms
from .models import Mensagem


class MensagemForm(forms.ModelForm):
    class Meta:
        model  = Mensagem
        fields = ['men_telefone', 'men_nome', 'men_dat', 'men_hora', 'men_ocorrencia', 'men_dia_semana', 'men_mensagem']
        widgets = {
            'men_telefone':  forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'id': 'id_men_telefone',
            }),
            'men_nome':      forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do contato',
            }),
            'men_dat':       forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'men_hora':      forms.TimeInput(format='%H:%M', attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'men_ocorrencia': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_men_ocorrencia',
            }),
            'men_dia_semana': forms.RadioSelect(attrs={
                'class': 'btn-check',
            }),
            'men_mensagem':  forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 150,
                'placeholder': 'Digite a mensagem (máx. 150 caracteres)',
                'id': 'id_men_mensagem',
            }),
        }
        labels = {
            'men_telefone':   'Telefone do Contato',
            'men_nome':       'Nome do Contato',
            'men_dat':        'Data Agendada',
            'men_hora':       'Hora Agendada',
            'men_ocorrencia': 'Ocorrência',
            'men_dia_semana': 'Dia da Semana',
            'men_mensagem':   'Mensagem',
        }
