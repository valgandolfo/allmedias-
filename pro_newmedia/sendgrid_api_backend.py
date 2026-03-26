"""
Backend de e-mail que usa a API HTTP do SendGrid (HTTPS, porta 443).
Evita bloqueio de SMTP (587/2525) em redes de datacenter.
Usa a mesma API Key que o SMTP: EMAIL_HOST_PASSWORD.
"""
import logging
import requests

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


class SendGridAPIBackend(BaseEmailBackend):
    """
    Envia e-mails via SendGrid API v3 (HTTPS). Não usa SMTP.
    Configuração: EMAIL_HOST_PASSWORD = sua API Key do SendGrid.
    """

    def __init__(self, api_key=None, password=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = (api_key or password or getattr(settings, 'EMAIL_HOST_PASSWORD', '') or "").strip()

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            try:
                self._send_one(message)
                sent += 1
            except Exception as e:
                logger.exception("SendGrid API: falha ao enviar e-mail: %s", e)
                if not self.fail_silently:
                    raise
        return sent

    def _send_one(self, message):
        if not self.api_key:
            raise ValueError("SendGrid API: EMAIL_HOST_PASSWORD (API Key) não definida.")

        to_list = [{"email": addr} for addr in message.to]
        from_email = message.from_email
        if isinstance(from_email, tuple):
            from_data = {"email": from_email[0], "name": from_email[1] or ""}
        else:
            from_data = {"email": from_email}

        payload = {
            "personalizations": [{"to": to_list}],
            "from": from_data,
            "subject": message.subject,
            "content": [{"type": "text/plain", "value": message.body}],
        }

        if hasattr(message, "alternatives") and message.alternatives:
            html_part = next((c for c in message.alternatives if c[1] == "text/html"), None)
            if html_part:
                payload["content"].append({"type": "text/html", "value": html_part[0]})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(
            SENDGRID_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
