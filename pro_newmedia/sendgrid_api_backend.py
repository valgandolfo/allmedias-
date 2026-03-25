"""
Backend de e-mail usando a API do SendGrid (não SMTP).
Mais confiável que SMTP em ambientes cloud (Railway, Heroku, etc).

Uso no settings.py / variável de ambiente:
    EMAIL_BACKEND=pro_newmedia.sendgrid_api_backend.SendGridAPIBackend
    EMAIL_HOST_PASSWORD=SG.sua_api_key_aqui
    DEFAULT_FROM_EMAIL=AllMedias <noreply@igeracao.com.br>
"""
import logging

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class SendGridAPIBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        # Aceita SENDGRID_API_KEY ou EMAIL_HOST_PASSWORD
        self.api_key = (
            getattr(settings, 'SENDGRID_API_KEY', None)
            or getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key:
            if not self.fail_silently:
                raise ValueError(
                    'SendGridAPIBackend: nenhuma API Key configurada. '
                    'Defina SENDGRID_API_KEY ou EMAIL_HOST_PASSWORD.'
                )
            logger.error('SendGridAPIBackend: API Key ausente, e-mails não enviados.')
            return 0

        try:
            import sendgrid as sg_module
            from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        except ImportError as exc:
            if not self.fail_silently:
                raise RuntimeError(
                    'Instale a dependência: pip install sendgrid'
                ) from exc
            return 0

        client = sg_module.SendGridAPIClient(api_key=self.api_key)
        num_sent = 0

        for message in email_messages:
            try:
                self._send(client, message)
                num_sent += 1
            except Exception as exc:
                logger.error(
                    'SendGridAPIBackend: falha ao enviar para %s — %s',
                    message.to,
                    exc,
                )
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, client, message):
        from sendgrid.helpers.mail import Mail, To, From, Subject, PlainTextContent, HtmlContent

        from_email = From(message.from_email)
        subject = Subject(message.subject)

        # Corpo texto puro
        plain_body = message.body or ' '

        # Corpo HTML (de alternatives se existir)
        html_body = None
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_body = content
                    break

        for recipient in message.to:
            mail = Mail()
            mail.from_email = from_email
            mail.subject = subject
            mail.to = To(recipient)
            mail.content = PlainTextContent(plain_body)

            if html_body:
                mail.add_content(HtmlContent(html_body))

            response = client.send(mail)

            status = getattr(response, 'status_code', None)
            if status and status >= 400:
                raise RuntimeError(
                    f'SendGrid retornou status {status} para {recipient}: '
                    f'{getattr(response, "body", "")}'
                )

            logger.info(
                'SendGridAPIBackend: e-mail enviado para %s (status %s)',
                recipient,
                status,
            )
