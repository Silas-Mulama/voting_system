from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import re

ADMISSION_NUMBER_REGEX = r'^[A-Z]+/\d{5}/\d{2}[A-Z]$'

class StudentAdminAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = None
        # Students: authenticate with admission_number
        if username and re.match(ADMISSION_NUMBER_REGEX, username):
            try:
                user = UserModel.objects.get(admission_number=username, is_student=True)
            except UserModel.DoesNotExist:
                return None
        # Admins: authenticate with email
        elif username and '@' in username:
            try:
                user = UserModel.objects.get(email__iexact=username, is_student=False)
            except UserModel.DoesNotExist:
                return None
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
