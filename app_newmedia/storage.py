import os
from django.core.files.storage import Storage
from django.conf import settings
from drive_upload import get_drive_service, upload_from_stream

class GoogleDriveStorage(Storage):
    """
    Custom Django Storage Backend para salvar imagens/arquivos no Google Drive
    usando google-api-python-client.
    """
    def __init__(self):
        self._service = None  # lazy — only connects on first use

    def _get_service(self):
        if self._service is None:
            credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
            token_path = os.path.join(settings.BASE_DIR, 'token.json')
            self._service = get_drive_service(credentials_path, token_path)
        return self._service

    @property
    def service(self):
        return self._get_service()

    def _open(self, name, mode='rb'):
        """Retorna o arquivo (bytes) baixado do Drive."""
        from io import BytesIO
        from django.core.files.base import ContentFile
        from googleapiclient.http import MediaIoBaseDownload

        if "//" in name:
            file_id = name.split("//")[0]
            request = self.service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            # Retorna um ContentFile que suporta .read()
            return ContentFile(fh.read())
            
        import os
        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        with open(os.path.join(media_root, name), 'rb') as local_file:
            return ContentFile(local_file.read())

    def _save(self, name, content):
        """
        Salva o arquivo `content` enviando para o Google Drive via API, 
        e retorna o nome que será armazenado no DB (uma string prefixada pelo File ID).
        """
        import logging
        logger = logging.getLogger(__name__)

        if hasattr(content, 'seek'):
            try:
                content.seek(0)
            except Exception:
                pass
        
        if hasattr(content, 'file') and hasattr(content.file, 'seek'):
            try:
                content.file.seek(0)
            except Exception:
                pass

        try:
            service = self.service
        except Exception as e:
            # Token expirado ou revogado → reseta conexão e relança com mensagem clara
            self._service = None
            logger.error(
                "[GoogleDriveStorage] Falha ao conectar ao Google Drive: %s\n"
                "→ O token OAuth expirou ou foi revogado.\n"
                "→ Para renovar: execute 'python drive_upload.py' localmente para gerar um novo token.json\n"
                "→ Em seguida atualize a variável GOOGLE_TOKEN_JSON no Railway com o conteúdo do novo token.json",
                e
            )
            raise IOError(
                "Google Drive Storage: token de autenticação inválido ou expirado. "
                "Renove o GOOGLE_TOKEN_JSON no Railway."
            ) from e

        try:
            file_id = upload_from_stream(service, content.file, name)
        except Exception as e:
            self._service = None  # força reconexão na próxima tentativa
            logger.error("[GoogleDriveStorage] Erro no upload para o Drive: %s", e)
            raise

        # Torna o arquivo público para visualização web na hora do upload
        try:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
        except Exception as e:
            # Em alguns Drives corporativos compartilhar externamente pode estar bloqueado
            logger.warning("[GoogleDriveStorage] Não foi possível tornar público: %s", e)

        # Retornamos "[id do arquivo]//[nome original]"
        return f"{file_id}//{name}"

    def exists(self, name):
        return False

    def url(self, name):
        """
        Retorna a URL pública que o browser usará para renderizar a imagem/pdf.
        """
        if "//" in name:
            file_id = name.split("//")[0]
            return f"https://drive.google.com/uc?id={file_id}&export=view"
        
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        name_clean = name.lstrip('/')
        return f"{media_url}{name_clean}"

    def delete(self, name):
        if "//" in name:
            file_id = name.split("//")[0]
            try:
                self.service.files().delete(fileId=file_id).execute()
            except Exception:
                pass
        
    def size(self, name):
        # Simplificando
        return 0
