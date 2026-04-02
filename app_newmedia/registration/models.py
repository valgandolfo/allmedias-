"""
Models de autenticação e perfil de usuário - AllMedias PWA
"""
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from app_newmedia.medias.utils import otimizar_imagem


def user_profile_photo_path(instance, filename):
    """
    Gera caminho para foto de perfil do usuário
    Ex: profiles/user_5/profile_photo.jpg
    """
    ext = os.path.splitext(filename)[1]
    return f'profiles/user_{instance.user.id}/profile_photo{ext}'


class UserProfile(models.Model):
    """
    Perfil estendido do usuário para AllMedias PWA
    Substitui a antiga TBPERFIL com funcionalidades adicionais
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='Usuário'
    )
    
    # ===================================================================
    # INFORMAÇÕES PESSOAIS
    # ===================================================================
    nome_completo = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Nome Completo'
    )
    
    telefone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Telefone'
    )
    
    data_nascimento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name='Data de Nascimento'
    )
    
    foto_perfil = models.ImageField(
        upload_to=user_profile_photo_path,
        blank=True,
        null=True,
        verbose_name='Foto de Perfil',
        help_text='Recomendado: 300x300px, máximo 2MB'
    )
    
    # ===================================================================
    # CONTROLE DE ACESSO E PLANO
    # ===================================================================
    dias_acesso = models.IntegerField(
        default=365, 
        verbose_name='Dias de Acesso',
        help_text='Quantidade de dias de acesso ao sistema'
    )
    
    data_expiracao = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name='Data de Expiração',
        help_text='Quando o acesso expira (calculado automaticamente)'
    )
    
    plano = models.CharField(
        max_length=20,
        choices=[
            ('gratuito', 'Gratuito'),
            ('premium', 'Premium'),
            ('vip', 'VIP'),
        ],
        default='gratuito',
        verbose_name='Plano de Assinatura'
    )
    
    # ===================================================================
    # PREFERÊNCIAS DO USUÁRIO
    # ===================================================================
    tema_escuro = models.BooleanField(
        default=False,
        verbose_name='Usar tema escuro'
    )
    
    notificacoes_email = models.BooleanField(
        default=True,
        verbose_name='Receber notificações por email'
    )
    
    compartilhamento_publico = models.BooleanField(
        default=False,
        verbose_name='Permitir compartilhamento público de mídias'
    )
    
    # ===================================================================
    # ESTATÍSTICAS E CONTROLE
    # ===================================================================
    total_midias = models.IntegerField(
        default=0,
        verbose_name='Total de Mídias',
        help_text='Contador automático de mídias do usuário'
    )
    
    total_anotacoes = models.IntegerField(
        default=0,
        verbose_name='Total de Anotações',
        help_text='Contador automático de anotações'
    )
    
    ultimo_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Último IP de Login'
    )
    
    # ===================================================================
    # TIMESTAMPS
    # ===================================================================
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação do Perfil'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        ordering = ['-data_criacao']

    def __str__(self):
        nome = self.nome_completo or self.user.get_full_name() or self.user.username
        return f"Perfil de {nome}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve save para otimizar imagem de perfil e calcular expiração
        """
        from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
        
        # Calcular data de expiração se não estiver definida
        if not self.data_expiracao and self.dias_acesso > 0:
            self.data_expiracao = timezone.now() + timezone.timedelta(days=self.dias_acesso)
        
        # Otimizar foto de perfil antes de salvar (apenas novos uploads)
        if self.foto_perfil:
            arquivo_file = getattr(self.foto_perfil, 'file', None)
            if isinstance(arquivo_file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                self.foto_perfil = self._otimizar_foto_perfil(arquivo_file)
        
        super().save(*args, **kwargs)

    def _otimizar_foto_perfil(self, foto):
        """
        Otimiza a foto de perfil usando a mesma rotina de mídias (Wasabi S3).
        """
        try:
            # Usar max_width/max_height de 300px como no código anterior
            # mas utilizando a rotina robusta de compressão unificada
            return otimizar_imagem(foto, max_width=300, max_height=300, quality=85)
            
        except Exception as e:
            print(f"Erro ao otimizar foto de perfil: {e}")
            return foto

    @property
    def dias_restantes(self):
        """
        Calcula quantos dias restam até a expiração
        """
        if not self.data_expiracao:
            return 0
        
        delta = self.data_expiracao - timezone.now()
        return max(0, delta.days)

    @property
    def acesso_ativo(self):
        """
        Verifica se o acesso ainda está ativo
        """
        if not self.data_expiracao:
            return True
        
        return timezone.now() < self.data_expiracao

    @property
    def foto_url(self):
        """
        Retorna URL da foto de perfil ou placeholder
        """
        if self.foto_perfil and hasattr(self.foto_perfil, 'url'):
            return self.foto_perfil.url
        
        # URL de avatar placeholder baseado no nome
        nome_inicial = self.nome_completo[0] if self.nome_completo else self.user.username[0].upper()
        return f"https://via.placeholder.com/300x300/0d6efd/FFFFFF?text={nome_inicial}"

    def incrementar_contador_midias(self):
        """
        Incrementa o contador de mídias
        """
        self.total_midias += 1
        self.save(update_fields=['total_midias'])

    def decrementar_contador_midias(self):
        """
        Decrementa o contador de mídias
        """
        if self.total_midias > 0:
            self.total_midias -= 1
            self.save(update_fields=['total_midias'])

    def incrementar_contador_anotacoes(self):
        """
        Incrementa o contador de anotações
        """
        self.total_anotacoes += 1
        self.save(update_fields=['total_anotacoes'])

    def decrementar_contador_anotacoes(self):
        """
        Decrementa o contador de anotações
        """
        if self.total_anotacoes > 0:
            self.total_anotacoes -= 1
            self.save(update_fields=['total_anotacoes'])

    def atualizar_ultimo_login(self, ip_address):
        """
        Atualiza o último IP de login
        """
        self.ultimo_login_ip = ip_address
        self.save(update_fields=['ultimo_login_ip'])

    def renovar_acesso(self, dias_adicionais):
        """
        Renova o acesso por mais dias
        """
        if self.data_expiracao:
            # Se já tem expiração, adiciona dias a partir da data atual ou da expiração (o que for maior)
            base_date = max(timezone.now(), self.data_expiracao)
        else:
            base_date = timezone.now()
        
        self.data_expiracao = base_date + timezone.timedelta(days=dias_adicionais)
        self.dias_acesso = dias_adicionais
        self.save()


# ===================================================================
# SIGNALS PARA CRIAÇÃO AUTOMÁTICA DE PERFIL
# ===================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um UserProfile quando um User é criado
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o UserProfile quando o User é salvo
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()