"""
Backend de autenticação por e-mail - AllMedias PWA
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailAuthBackend(ModelBackend):
    """
    Autentica usando e-mail no lugar de username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # O campo 'username' recebe o e-mail digitado no formulário
        email = username
        if not email or not password:
            return None

        try:
            user = User.objects.get(email__iexact=email.strip())
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Em caso de duplicata, pega o mais recente ativo
            user = User.objects.filter(
                email__iexact=email.strip(), is_active=True
            ).order_by('-date_joined').first()
            if not user:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
