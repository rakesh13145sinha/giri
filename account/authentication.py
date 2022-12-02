from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
# from matrimonyapp.models import *


class AuthBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(email = username)
            return user
        except UserModel.DoesNotExist:
            try:
                user = UserModel._default_manager.get(username = username)
                return user
            except UserModel.DoesNotExist:
                 # user_obj = UserBasicDetails.objects.get(phone_number=username)
                # user = UserModel._default_manager.get(username=user_obj)
                return #user
        else:
            return None

    def get_user(self,user_id):
        try:
            UserModel = get_user_model()
            return UserModel._default_manager.get(pk = user_id)
        except UserModel.DoesNotExist:
            return None
			