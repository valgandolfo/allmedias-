"""
Admin para models de autenticação - AllMedias PWA
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin personalizado para UserProfile
    """
    list_display = [
        'user', 'nome_completo', 'telefone', 'plano', 
        'total_midias', 'total_anotacoes', 'acesso_ativo', 'data_criacao'
    ]
    list_filter = ['plano', 'tema_escuro', 'data_criacao']
    search_fields = ['user__email', 'nome_completo', 'telefone']
    readonly_fields = ['data_criacao', 'data_atualizacao', 'ultimo_login_ip']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Pessoais', {
            'fields': ('nome_completo', 'telefone', 'data_nascimento', 'foto_perfil')
        }),
        ('PIX', {
            'fields': ('pix_nome', 'pix_chave', 'pix_favorecido', 'pix_banco'),
            'classes': ('collapse',)
        }),
        ('Acesso e Plano', {
            'fields': ('plano', 'dias_acesso', 'data_expiracao')
        }),
        ('Preferências', {
            'fields': ('tema_escuro', 'notificacoes_email', 'compartilhamento_publico'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('total_midias', 'total_anotacoes'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('ultimo_login_ip', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


# Personalizar UserAdmin para incluir link para perfil
class CustomUserAdmin(UserAdmin):
    """
    Admin personalizado para User
    """
    list_display = UserAdmin.list_display + ('get_profile_link',)
    
    def get_profile_link(self, obj):
        if hasattr(obj, 'profile'):
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:registration_userprofile_change', args=[obj.profile.id])
            return format_html('<a href="{}">Ver Perfil</a>', url)
        return 'Sem perfil'
    get_profile_link.short_description = 'Perfil'

# Re-registrar User com admin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)