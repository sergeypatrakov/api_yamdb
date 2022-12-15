from typing import Tuple

from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLES: Tuple[Tuple[str]] = (
    ("user", "Аутентифицированный пользователь"),
    ("moderator", "Модератор"),
    ("admin", "Администратор"),
)


class User(AbstractUser):
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name="Роль",
        max_length=32,
        choices=USER_ROLES,
        default='user',
    )
