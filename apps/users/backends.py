from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username_or_email=None, password=None, **kwargs):
        UserModel = get_user_model()

        user = None

        try:
            if username_or_email:
                user = UserModel.objects.get(username=username_or_email)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=username_or_email)
            except UserModel.DoesNotExist:
                return None

        if user:
            if user.check_password(password):
                if user.is_active:
                    return user
                else:
                    return None
        return None


