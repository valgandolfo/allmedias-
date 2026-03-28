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
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        token_path = os.path.join(settings.BASE_DIR, 'token.json')
        self.service = get_drive_service(credentials_path, token_path)

    def _save(self, name, content):
        """
        Salva o arquivo `content` enviando para o Google Drive via API, 
        e retorna o nome que será armazenado no DB (uma string prefixada pelo File ID).
        """
        # Como o Django manda InMemoryUploadedFile ou um TemporaryUploadedFile, 
        # enviamos o objeto diretamente para o uploader IoBase.
        file_id = upload_from_stream(self.service, content.file, name)
        
        # A API Google Drive e a lógica web mudam as permissões:
        try:
            # Torna o arquivo público para visualização web na hora do upload
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
        except Exception as e:
            # Em alguns Drives corporativos compartilhar externamente pode estar bloqueado
            print(f"Não foi possível deixar público automaticamente: {e}")

        # Retornamos "[id do arquivo]//[nome original]" para preservarmos o nome original
        # mas podermos fazer retrieve só pelo ID no método url()
        return f"{file_id}//{name}"

    def exists(self, name):
        # Para evitar verificações constantes de existência via API,
        # simplificamos retornando False (o Django gerará outro nome apenas se file_id//name colidisse, o que é quase impossível devido ao File ID único).
        return False

    def url(self, name):
        """
        Retorna a URL pública que o browser usará para renderizar a imagem/pdf.
        O Drive disponibiliza links fáceis como uc?id=...
        """
        if "//" in name:
            file_id = name.split("//")[0]
            # Formato antigo era mais compatível para imagens; webContentLink também é uma boa pedida.
            # uc?id=X&export=view funciona melhor nas tags <img>.
            return f"https://drive.google.com/uc?id={file_id}&export=view"
        
        # Em caso de arquivos velhos do Wasabi que ainda não têm "//", nós repassamos sem modificar 
        # (mas eles devem quebrar sem o S3 configurado, é esperado)
        return name

    def delete(self, name):
        if "//" in name:
            file_id = name.split("//")[0]
            try:
                self.service.files().delete(fileId=file_id).execute()
            except Exception as e:
                pass
        
    def size(self, name):
        # Simplificando
        return 0
