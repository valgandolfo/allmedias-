"""
Models de mídias - NewMedia PWA
"""
import os
import uuid
import logging
from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

logger = logging.getLogger(__name__)


def user_media_path(instance, filename):
    """
    Gera caminho no storage segregando por usuário.
    Ex: user_5/medias/<uuid>.ext
    """
    ext = os.path.splitext(filename)[1] or '.bin'
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

    descricao = models.CharField(max_length=100, verbose_name='Descrição')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name='Tipo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='concluido', verbose_name='Status')
    tags = models.CharField(max_length=500, blank=True, null=True, verbose_name='Tags')
    arquivo = models.FileField(upload_to=user_media_path, blank=True, null=True, verbose_name='Arquivo')
    miniatura = models.ImageField(upload_to=user_media_path, blank=True, null=True, verbose_name='Miniatura')
    tamanho = models.CharField(max_length=20, blank=True, null=True, verbose_name='Tamanho')
    favorito = models.BooleanField(default=False, verbose_name='Favorito')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='midias', verbose_name='Usuário')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Mídia'
        verbose_name_plural = 'Mídias'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"

    def save(self, *args, **kwargs):
        from django.template.defaultfilters import filesizeformat

        # Só processa se for um novo arquivo (ainda não enviado ao storage)
        is_novo = self.arquivo and not getattr(self.arquivo, '_committed', True)

        if is_novo:
            # Processamento exclusivo para imagens (otimiza antes de medir o tamanho)
            if self._arquivo_eh_imagem():
                self._processar_imagem()

            # Captura tamanho APÓS otimização — reflete o arquivo real enviado ao Wasabi
            try:
                self.tamanho = filesizeformat(self.arquivo.size)
            except Exception:
                self.tamanho = None

        super().save(*args, **kwargs)

    # ------------------------------------------------------------------ #
    # Métodos internos                                                     #
    # ------------------------------------------------------------------ #

    def _arquivo_eh_imagem(self):
        """Verifica extensão antes do upload (antes de _committed=True)."""
        try:
            nome = self.arquivo.file.name if hasattr(self.arquivo, 'file') else self.arquivo.name
            return os.path.splitext(nome)[1].lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic')
        except Exception:
            return False

    def _processar_imagem(self):
        """
        Otimiza a imagem e gera miniatura.
        Substitui self.arquivo e self.miniatura por SimpleUploadedFile
        — o Django cuida do upload para o S3 automaticamente no pre_save.
        """
        try:
            from .utils import otimizar_imagem, gerar_miniatura

            # Stream raw do arquivo enviado
            raw = getattr(self.arquivo, 'file', self.arquivo)
            raw.seek(0)

            # 1. Otimiza imagem principal
            otimizada = otimizar_imagem(raw)
            otimizada.seek(0)

            # 2. Gera miniatura a partir da versão otimizada (stream ainda intacta)
            thumb = gerar_miniatura(otimizada)

            # 3. Substitui self.arquivo pelo arquivo otimizado
            #    Django fará o upload para o S3 via FileField.pre_save
            otimizada.seek(0)
            self.arquivo = SimpleUploadedFile(
                'imagem.jpg',
                otimizada.read(),
                content_type='image/jpeg',
            )

            # 4. Define miniatura (Django também faz o upload automaticamente)
            if thumb:
                thumb.seek(0)
                self.miniatura = SimpleUploadedFile(
                    'miniatura.jpg',
                    thumb.read(),
                    content_type='image/jpeg',
                )
                logger.info("[Midia] Miniatura gerada com sucesso.")

            logger.info("[Midia] Imagem otimizada com sucesso.")

        except Exception as e:
            logger.error("[Midia] Erro ao processar imagem: %s", e, exc_info=True)

    # ------------------------------------------------------------------ #
    # Properties públicas                                                  #
    # ------------------------------------------------------------------ #

    def get_tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def is_imagem(self):
        if not self.arquivo:
            return False
        ext = os.path.splitext(self.arquivo.name)[1].lower()
        return ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic')

    @property
    def is_pdf(self):
        if not self.arquivo:
            return False
        return os.path.splitext(self.arquivo.name)[1].lower() == '.pdf'
