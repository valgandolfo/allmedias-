"""
Models de mídias - NewMedia PWA
"""
import os
import uuid
import logging
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def user_media_path(instance, filename):
    """
    Gera caminho no storage segregando por usuário.
    Ex: user_5/medias/<uuid>.ext
    """
    ext = os.path.splitext(filename)[1] or ''
    user_id = getattr(instance, 'usuario_id', None)
    user_prefix = f"user_{user_id}" if user_id else "user_unknown"
    return f"{user_prefix}/medias/{uuid.uuid4()}{ext}"


class Midia(models.Model):
    """
    Mídia do usuário (fotos, PDFs, vídeos, áudios, documentos, etc.)
    """
    TIPO_CHOICES = [
        ('foto', 'Foto'),
        ('pdf', 'PDF'),
        ('documento', 'Documento'),
        ('texto', 'Texto'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
        ('outro', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Enviando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro no Upload'),
    ]

    descricao = models.CharField(
        max_length=100,
        verbose_name='Descrição'
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='concluido',
        verbose_name='Status'
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Tags'
    )
    arquivo = models.FileField(
        upload_to=user_media_path,
        blank=True,
        null=True,
        verbose_name='Arquivo'
    )
    miniatura = models.ImageField(
        upload_to=user_media_path,
        blank=True,
        null=True,
        verbose_name='Miniatura'
    )
    tamanho = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Tamanho'
    )
    favorito = models.BooleanField(
        default=False,
        verbose_name='Favorito'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='midias',
        verbose_name='Usuário'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Mídia'
        verbose_name_plural = 'Mídias'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"

    def save(self, *args, **kwargs):
        from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
        from django.template.defaultfilters import filesizeformat

        if self.arquivo:
            arquivo_file = getattr(self.arquivo, 'file', None)
            is_novo_upload = isinstance(arquivo_file, (InMemoryUploadedFile, TemporaryUploadedFile))

            if is_novo_upload:
                # Otimizar se for imagem
                if self.is_imagem:
                    try:
                        from .utils import otimizar_imagem, gerar_miniatura
                        # Optimizes main image
                        self.arquivo = otimizar_imagem(self.arquivo)
                        
                        # Generate thumbnail
                        thumb_file = gerar_miniatura(self.arquivo)
                        if thumb_file:
                            self.miniatura = thumb_file
                    except Exception as e:
                        logger.error(f"Erro ao otimizar imagem no save: {e}")

                # Gravar tamanho enquanto arquivo ainda está em memória/disco
                try:
                    tamanho_bytes = self.arquivo.size
                    self.tamanho = filesizeformat(tamanho_bytes)
                except Exception:
                    self.tamanho = None

        super().save(*args, **kwargs)

    def get_tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def is_imagem(self):
        if not self.arquivo:
            return False
        ext = os.path.splitext(self.arquivo.name)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic']

    @property
    def is_pdf(self):
        if not self.arquivo:
            return False
        return os.path.splitext(self.arquivo.name)[1].lower() == '.pdf'
