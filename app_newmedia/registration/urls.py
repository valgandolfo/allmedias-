"""
URLs de autenticação - AllMedias PWA
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# URLs de autenticação do AllMedias PWA

urlpatterns = [
    # ===================================================================
    # AUTENTICAÇÃO BÁSICA
    # ===================================================================
    
    # Login
    path('login/', views.AllMediasLoginView.as_view(), name='login'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
    
    # Registro
    path('register/', views.AllMediasRegistrationView.as_view(), name='register'),
    
    # ===================================================================
    # RECUPERAÇÃO DE SENHA
    # ===================================================================
    
    # Solicitar reset de senha
    path('password-reset/', 
         views.AllMediasPasswordResetView.as_view(), 
         name='password_reset'),
    
    # Confirmação de envio de email
    path('password-reset/done/', 
         views.AllMediasPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    
    # Link do email - definir nova senha
    path('password-reset/confirm/<uidb64>/<token>/', 
         views.AllMediasPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    # Senha alterada com sucesso
    path('password-reset/complete/', 
         views.AllMediasPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    
    # ===================================================================
    # PERFIL DE USUÁRIO
    # ===================================================================
    
    # Visualizar perfil
    path('profile/', views.profile_view, name='profile'),
    
    # Editar perfil
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Configurações da conta
    path('settings/', views.account_settings_view, name='account_settings'),
    
    # ===================================================================
    # AJAX / API ENDPOINTS
    # ===================================================================
    
    # Deletar foto de perfil
    path('api/profile/delete-photo/', 
         views.profile_delete_photo_view, 
         name='api_delete_photo'),
    
    # Verificar força da senha
    path('api/check-password/', 
         views.check_password_strength, 
         name='api_check_password'),
    
    # Verificar disponibilidade de email
    path('api/check-email/', 
         views.check_email_availability, 
         name='api_check_email'),
    
    # ===================================================================
    # DEBUG (apenas em desenvolvimento)
    # ===================================================================
    
    # Informações do usuário para debug
    path('debug/user-info/', views.debug_user_info, name='debug_user_info'),
]

# URLs alternativas (compatibilidade com Django padrão)
auth_urlpatterns = [
    # Django Auth URLs padrão para compatibilidade
    path('accounts/login/', views.AllMediasLoginView.as_view()),
    path('accounts/logout/', views.logout_view),
    path('accounts/signup/', views.AllMediasRegistrationView.as_view()),
    path('accounts/profile/', views.profile_view),
]

# Adicionar URLs alternativas
urlpatterns += auth_urlpatterns