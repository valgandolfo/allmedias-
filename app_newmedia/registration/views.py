"""
Views de autenticação - AllMedias PWA
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, 
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .forms import (
    AllMediasLoginForm,
    AllMediasRegistrationForm, 
    AllMediasPasswordResetForm,
    AllMediasSetPasswordForm,
    UserProfileForm
)
from .models import UserProfile


def get_client_ip(request):
    """
    Obtém o IP real do cliente (considerando proxies)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AllMediasLoginView(LoginView):
    """
    View customizada de login do AllMedias
    """
    form_class = AllMediasLoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        Redireciona para a próxima página ou home
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('home')
    
    def form_valid(self, form):
        """
        Login bem-sucedido - configurar sessão e logging
        """
        # Configurar "lembrar-me"
        remember_me = form.cleaned_data.get('remember_me', False)
        
        if not remember_me:
            # Sessão expira quando fechar o navegador
            self.request.session.set_expiry(0)
        else:
            # Sessão de 30 dias
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        
        # Login padrão
        response = super().form_valid(form)
        
        # Atualizar dados do perfil
        user = self.request.user
        if hasattr(user, 'profile'):
            user.profile.atualizar_ultimo_login(get_client_ip(self.request))
        
        # Mensagem de boas-vindas
        nome = user.profile.nome_completo if hasattr(user, 'profile') and user.profile.nome_completo else user.username
        messages.success(
            self.request, 
            f'Bem-vindo de volta, {nome}! 🎉'
        )
        
        return response
    
    def form_invalid(self, form):
        """
        Login falhou - mensagem personalizada
        """
        messages.error(
            self.request,
            'E-mail ou senha incorretos. Verifique os dados e tente novamente.'
        )
        return super().form_invalid(form)


class AllMediasLogoutView(LogoutView):
    """
    View customizada de logout
    """
    template_name = 'registration/logged_out.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Adiciona mensagem de logout
        """
        if request.user.is_authenticated:
            nome = request.user.profile.nome_completo if hasattr(request.user, 'profile') and request.user.profile.nome_completo else request.user.username
            messages.info(request, f'Até logo, {nome}! Volte sempre.')
        
        return super().dispatch(request, *args, **kwargs)


class AllMediasRegistrationView(CreateView):
    """
    View de registro de usuário
    """
    model = User
    form_class = AllMediasRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Redireciona usuários já logados
        """
        if request.user.is_authenticated:
            messages.info(request, 'Você já está logado!')
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Registro bem-sucedido
        """
        response = super().form_valid(form)
        
        # Mensagem de sucesso
        messages.success(
            self.request,
            f'Conta criada com sucesso! '
            f'Faça login com seu e-mail: {form.cleaned_data["email"]}'
        )
        
        # Log opcional do registro
        user = form.instance
        print(f"Novo usuário registrado: {user.email} (ID: {user.id})")
        
        return response
    
    def form_invalid(self, form):
        """
        Erro no registro
        """
        messages.error(
            self.request,
            'Erro no cadastro. Verifique os dados e tente novamente.'
        )
        return super().form_invalid(form)


class AllMediasPasswordResetView(PasswordResetView):
    """
    View para solicitar reset de senha
    """
    form_class = AllMediasPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    
    def form_valid(self, form):
        """
        Email de reset enviado
        """
        messages.success(
            self.request,
            'E-mail de recuperação enviado! Verifique sua caixa de entrada e spam.'
        )
        return super().form_valid(form)


class AllMediasPasswordResetDoneView(PasswordResetDoneView):
    """
    View de confirmação de envio de email
    """
    template_name = 'registration/password_reset_done.html'


class AllMediasPasswordResetConfirmView(PasswordResetConfirmView):
    """
    View para definir nova senha
    """
    form_class = AllMediasSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        """
        Nova senha definida
        """
        messages.success(
            self.request,
            'Senha alterada com sucesso! Você pode fazer login com a nova senha.'
        )
        return super().form_valid(form)


class AllMediasPasswordResetCompleteView(PasswordResetCompleteView):
    """
    View de confirmação de reset completo
    """
    template_name = 'registration/password_reset_complete.html'


@login_required
def profile_view(request):
    """
    View para exibir perfil do usuário
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Criar perfil se não existir
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'registration/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    View para editar perfil do usuário
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso! ✅')
            return redirect('profile')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'registration/profile_edit.html', context)


@login_required
def profile_delete_photo_view(request):
    """
    View para deletar foto de perfil (AJAX)
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            if profile.foto_perfil:
                # Deletar arquivo físico
                profile.foto_perfil.delete(save=False)
                profile.foto_perfil = None
                profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Foto removida com sucesso!',
                    'new_photo_url': profile.foto_url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhuma foto para remover.'
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao remover foto: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@csrf_exempt
@login_required
def check_password_strength(request):
    """
    API para verificar força da senha (AJAX)
    """
    if request.method == 'POST':
        import json
        
        try:
            data = json.loads(request.body)
            password = data.get('password', '')
            
            # Análise de força
            score = 0
            feedback = []
            
            if len(password) >= 8:
                score += 1
            else:
                feedback.append('Pelo menos 8 caracteres')
            
            if any(c.isupper() for c in password):
                score += 1
            else:
                feedback.append('Pelo menos uma letra maiúscula')
            
            if any(c.islower() for c in password):
                score += 1
            else:
                feedback.append('Pelo menos uma letra minúscula')
            
            if any(c.isdigit() for c in password):
                score += 1
            else:
                feedback.append('Pelo menos um número')
            
            # Caracteres especiais (opcional, +1 ponto extra)
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if any(c in special_chars for c in password):
                score += 1
                feedback.append('✓ Contém caracteres especiais (ótimo!)')
            
            # Classificação
            if score <= 1:
                strength = 'very-weak'
                strength_text = 'Muito fraca'
            elif score == 2:
                strength = 'weak'
                strength_text = 'Fraca'
            elif score == 3:
                strength = 'medium'
                strength_text = 'Média'
            elif score == 4:
                strength = 'strong'
                strength_text = 'Forte'
            else:
                strength = 'very-strong'
                strength_text = 'Muito forte'
            
            return JsonResponse({
                'strength': strength,
                'strength_text': strength_text,
                'score': score,
                'max_score': 5,
                'feedback': feedback
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método não permitido'})


@login_required
def account_settings_view(request):
    """
    View para configurações da conta
    """
    profile = request.user.profile
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'registration/account_settings.html', context)


def check_email_availability(request):
    """
    API para verificar se email está disponível (AJAX)
    """
    email = request.GET.get('email', '').lower().strip()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email inválido'})
    
    # Verificar se existe
    exists = User.objects.filter(email=email).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'E-mail disponível' if not exists else 'E-mail já cadastrado'
    })


@method_decorator(never_cache, name='dispatch')
class AllMediasLoginRequiredMixin:
    """
    Mixin para views que requerem login
    Com redirecionamento personalizado e mensagens
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request, 
                'Você precisa fazer login para acessar esta página.'
            )
            return redirect('login')
        
        # Verificar se a conta não expirou
        if hasattr(request.user, 'profile') and not request.user.profile.acesso_ativo:
            messages.error(
                request,
                'Seu acesso expirou. Entre em contato para renovar.'
            )
            logout(request)
            return redirect('login')
        
        return super().dispatch(request, *args, **kwargs)


# ===================================================================
# VIEWS AUXILIARES PARA DEBUGGING (apenas em desenvolvimento)
# ===================================================================
def debug_user_info(request):
    """
    View para debug de informações do usuário (apenas DEV)
    """
    from django.conf import settings
    
    if not settings.DEBUG:
        return JsonResponse({'error': 'Not available in production'})
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'})
    
    user = request.user
    profile_data = {}
    
    if hasattr(user, 'profile'):
        profile = user.profile
        profile_data = {
            'id': profile.id,
            'nome_completo': profile.nome_completo,
            'telefone': profile.telefone,
            'data_nascimento': profile.data_nascimento,
            'dias_restantes': profile.dias_restantes,
            'acesso_ativo': profile.acesso_ativo,
            'total_midias': profile.total_midias,
            'total_anotacoes': profile.total_anotacoes,
            'ultimo_login_ip': profile.ultimo_login_ip,
            'plano': profile.plano,
        }
    
    data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        },
        'profile': profile_data,
        'session_info': {
            'session_key': request.session.session_key,
            'session_expiry': request.session.get_expiry_date(),
            'ip_address': get_client_ip(request),
        }
    }
    
    return JsonResponse(data, indent=2)