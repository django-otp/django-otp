from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class TestUserManager(BaseUserManager):
    def create_user(self, identifier, password=None):
        if password is not None:
            password = make_password(password)

        return self.create(identifier=identifier, password=password)

    create_superuser = create_user


class TestUser(AbstractBaseUser):
    identifier = models.CharField(max_length=40, unique=True, db_index=True)

    objects = TestUserManager()

    USERNAME_FIELD = 'identifier'

    def get_full_name(self):
        return self.identifier

    def get_short_name(self):
        return self.identifier
