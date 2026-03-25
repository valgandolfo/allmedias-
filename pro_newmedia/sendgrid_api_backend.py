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

SENDGRID_TIMEOUT = 15  # segundos


class SendGridAPIBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = (
            getattr(settings, 'SENDGRID_API_KEY', None)
            or getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        )

    def _get_client(self):
        import sendgrid as sg_module
        client = sg_module.SendGridAPIClient(api_key=self.api_key)
        # Aplica timeout na conexão HTTP para não travar
        client.client.timeout = SENDGRID_TIMEOUT
        return client

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key:
            msg = (
                'SendGridAPIBackend: API Key não configurada. '
                'Defina SENDGRID_API_KEY ou EMAIL_HOST_PASSWORD.'
            )
            logger.error(msg)
            if not self.fail_silently:
                raise ValueError(msg)
            return 0

        try:
            client = self._get_client()
        except ImportError as exc:
            if not self.fail_silently:
                raise RuntimeError('Instale a dependência: pip install sendgrid') from exc
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                self._send(client, message)
                num_sent += 1
            except Exception as exc:
                logger.error(
                    'SendGridAPIBackend: falha ao enviar para %s — %s',
                    message.to, exc,
                )
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, client, message):
        from sendgrid.helpers.mail import (
            Mail,
            To,
            From,
            PlainTextContent,
            HtmlContent,
            TrackingSettings,
            ClickTracking,
            OpenTracking,
        )

        from_email = From(message.from_email)
        plain_body = message.body or ' '

        html_body = None
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_body = content
                    break

        for recipient in message.to:
            mail = Mail()
            mail.from_email = from_email
            mail.subject = message.subject
            mail.to = To(recipient)
            mail.content = PlainTextContent(plain_body)

            if html_body:
                mail.add_content(HtmlContent(html_body))

            # Evita reescrita de links (ex.: uid/token quebrados como "NA")
            mail.tracking_settings = TrackingSettings(
                click_tracking=ClickTracking(enable=False, enable_text=False),
                open_tracking=OpenTracking(enable=False),
            )

            response = client.send(mail)

            status = getattr(response, 'status_code', None)
            if status and status >= 400:
                raise RuntimeError(
                    f'SendGrid retornou HTTP {status} para {recipient}: '
                    f'{getattr(response, "body", "")}'
                )

            logger.info(
                'SendGridAPIBackend: e-mail enviado para %s (HTTP %s)',
                recipient, status,
            )
