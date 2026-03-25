"""
Forms de autenticação - AllMedias PWA
"""
import re
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, 
    UserCreationForm, 
    PasswordResetForm,
    SetPasswordForm
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from .models import UserProfile


class AllMediasLoginForm(AuthenticationForm):
    """
    Form customizado de login do AllMedias
    - Email como username
    - Checkbox "Lembrar-me"
    - Validações personalizadas
    """
    username = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_username',
            'placeholder': 'seu@email.com',
            'autocomplete': 'off',
            'autofocus': True
        }),
        label='E-mail',
        help_text='Digite seu e-mail de cadastro'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_password',
            'placeholder': '••••••••',
            'autocomplete': 'off'
        }),
        label='Senha',
        help_text='Digite sua senha'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_remember'
        }),
        label='Lembrar-me por 30 dias'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove mensagens de erro padrão confusas
        self.error_messages['invalid_login'] = (
            'E-mail ou senha incorretos. Verifique os dados e tente novamente.'
        )
        self.error_messages['inactive'] = (
            'Esta conta foi desativada. Entre em contato com o administrador.'
        )
    
    def clean_username(self):
        """
        Valida e normaliza o email
        """
        email = self.cleaned_data.get('username')
        if email:
            email = email.lower().strip()
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError('Digite um e-mail válido.')
        return email
    
    def clean(self):
        """
        Validação personalizada do login
        """
        cleaned_data = super().clean()
        
        # Se passou na validação padrão, configurar "lembrar-me"
        if cleaned_data and not self.errors:
            remember_me = cleaned_data.get('remember_me', False)
            if remember_me:
                # Será usado na view para configurar sessão longa
                self.remember_user = True
        
        return cleaned_data


class AllMediasRegistrationForm(UserCreationForm):
    """
    Form de registro customizado do AllMedias
    - Email obrigatório e único
    - Validação robusta de senha
    - Campos adicionais opcionais
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_email',
            'placeholder': 'seu@email.com'
        }),
        label='E-mail',
        help_text='Será usado para login e recuperação de senha'
    )
    
    nome_completo = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_nome_completo',
            'placeholder': 'Seu nome completo (opcional)'
        }),
        label='Nome Completo (opcional)',
        help_text='Como você gostaria de ser chamado'
    )
    
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_telefone',
            'placeholder': '(11) 99999-9999',
            'data-mask': '(00) 00000-0000'
        }),
        label='Telefone (opcional)',
        help_text='Para contato e recuperação de conta'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password1',
            'placeholder': '••••••••'
        }),
        label='Senha',
        help_text='Mínimo 8 caracteres, com letras e números'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password2',
            'placeholder': '••••••••'
        }),
        label='Confirmar Senha',
        help_text='Digite a mesma senha novamente'
    )
    
    aceito_termos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_aceito_termos'
        }),
        label='Li e aceito os termos de uso e política de privacidade',
        error_messages={
            'required': 'Você deve aceitar os termos para se cadastrar.'
        }
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove mensagens de erro confusas do Django
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Remove o campo username (usaremos email)
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_email(self):
        """
        Valida se o email é único e válido
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            
            # Validar formato
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError('Digite um e-mail válido.')
            
            # Verificar se já existe
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    'Este e-mail já está cadastrado. '
                    'Tente fazer login ou use "Esqueci minha senha".'
                )
        
        return email
    
    def clean_telefone(self):
        """
        Valida e normaliza telefone
        """
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remover caracteres não numéricos
            telefone_limpo = re.sub(r'\D', '', telefone)
            
            # Validar tamanho (10 ou 11 dígitos)
            if len(telefone_limpo) not in [10, 11]:
                raise forms.ValidationError(
                    'Telefone deve ter 10 ou 11 dígitos.'
                )
            
            # Formatar (11) 99999-9999
            if len(telefone_limpo) == 11:
                telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            else:
                telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        
        return telefone
    
    def clean_password1(self):
        """
        Validação robusta de senha
        """
        password = self.cleaned_data.get('password1')
        
        if password:
            # Validações personalizadas
            errors = []
            
            if len(password) < 8:
                errors.append('A senha deve ter pelo menos 8 caracteres.')
            
            if not re.search(r'[A-Z]', password):
                errors.append('A senha deve conter pelo menos uma letra maiúscula.')
            
            if not re.search(r'[a-z]', password):
                errors.append('A senha deve conter pelo menos uma letra minúscula.')
            
            if not re.search(r'\d', password):
                errors.append('A senha deve conter pelo menos um número.')
            
            # Verificar se não é muito comum
            senhas_comuns = [
                '12345678', 'password', '123456789', 'qwerty123',
                'abc123456', 'senha123', 'admin123'
            ]
            if password.lower() in senhas_comuns:
                errors.append('Esta senha é muito comum. Escolha uma senha mais segura.')
            
            if errors:
                raise forms.ValidationError(errors)
        
        return password
    
    def save(self, commit=True):
        """
        Cria usuário com email como username e preenche perfil
        """
        # Criar usuário usando email como username
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Preencher dados do perfil (criado automaticamente pelo signal)
            profile = user.profile
            profile.nome_completo = self.cleaned_data.get('nome_completo', '')
            profile.telefone = self.cleaned_data.get('telefone', '')
            profile.save()
        
        return user


class AllMediasPasswordResetForm(PasswordResetForm):
    """
    Form customizado de recuperação de senha
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_email',
            'placeholder': 'seu@email.com',
            'autofocus': True
        }),
        label='E-mail',
        help_text='Digite o e-mail da sua conta'
    )
    
    def clean_email(self):
        """
        Valida se o email existe no sistema
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            
            # Verificar se existe usuário com este email
            if not User.objects.filter(email=email, is_active=True).exists():
                raise forms.ValidationError(
                    'Não encontramos uma conta ativa com este e-mail. '
                    'Verifique se digitou corretamente ou cadastre-se.'
                )
        
        return email

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Garante URL absoluta correta no e-mail (evita uid corrompido por
        rastreamento SendGrid / clientes de e-mail com {% url %}).
        """
        path = reverse(
            'password_reset_confirm',
            kwargs={'uidb64': context['uid'], 'token': context['token']},
        )
        context = {
            **context,
            'password_reset_url': f"{context['protocol']}://{context['domain']}{path}",
        }
        super().send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=html_email_template_name,
        )


class AllMediasSetPasswordForm(SetPasswordForm):
    """
    Form para definir nova senha (recuperação)
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_new_password1',
            'placeholder': '••••••••',
            'autofocus': True
        }),
        label='Nova Senha',
        help_text='Mínimo 8 caracteres, com letras e números'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'id_new_password2',
            'placeholder': '••••••••'
        }),
        label='Confirmar Nova Senha',
        help_text='Digite a mesma senha novamente'
    )
    
    def clean_new_password1(self):
        """
        Usa a mesma validação do form de registro
        """
        password = self.cleaned_data.get('new_password1')
        
        if password:
            # Validações personalizadas (mesmas do registro)
            errors = []
            
            if len(password) < 8:
                errors.append('A senha deve ter pelo menos 8 caracteres.')
            
            if not re.search(r'[A-Z]', password):
                errors.append('A senha deve conter pelo menos uma letra maiúscula.')
            
            if not re.search(r'[a-z]', password):
                errors.append('A senha deve conter pelo menos uma letra minúscula.')
            
            if not re.search(r'\d', password):
                errors.append('A senha deve conter pelo menos um número.')
            
            if errors:
                raise forms.ValidationError(errors)
        
        return password


class UserProfileForm(forms.ModelForm):
    """
    Form para edição de perfil de usuário
    """
    nome_completo = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo'
        }),
        label='Nome Completo'
    )
    
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(11) 99999-9999',
            'data-mask': '(00) 00000-0000'
        }),
        label='Telefone'
    )
    
    data_nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Data de Nascimento'
    )
    
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Foto de Perfil',
        help_text='Recomendado: 300x300px, máximo 2MB'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'nome_completo', 'telefone', 'data_nascimento', 'foto_perfil',
            'tema_escuro', 'notificacoes_email', 'compartilhamento_publico'
        ]
        widgets = {
            'tema_escuro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notificacoes_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'compartilhamento_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_foto_perfil(self):
        """
        Valida formato da foto de perfil. O limite de tamanho foi removido
        pois a imagem é processada e otimizada pelo backend.
        """
        foto = self.cleaned_data.get('foto_perfil')
        
        if foto:
            # Verificar formato
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if foto.content_type not in allowed_types:
                raise forms.ValidationError(
                    'Formato de imagem não suportado. Use JPEG, PNG, GIF ou WebP.'
                )
        
        return foto
    
    def clean_telefone(self):
        """
        Valida e normaliza telefone (mesmo do registro)
        """
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone_limpo = re.sub(r'\D', '', telefone)
            
            if len(telefone_limpo) not in [10, 11]:
                raise forms.ValidationError(
                    'Telefone deve ter 10 ou 11 dígitos.'
                )
            
            if len(telefone_limpo) == 11:
                telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            else:
                telefone = f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        
        return telefone