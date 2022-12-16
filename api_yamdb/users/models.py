from typing import Tuple

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_ROLE: str = "user"
    MODERATOR_ROLE: str = "moderator"
    ADMIN_ROLE: str = "admin"
    ROLE_CHOICES: Tuple[Tuple[str, ...], ...] = (
        (USER_ROLE, "Аутентифицированный пользователь"),
        (MODERATOR_ROLE, "Модератор"),
        (ADMIN_ROLE, "Администратор"),
    )

    bio = models.TextField(
        verbose_name="Биография",
        blank=True,
    )
    role = models.CharField(
        verbose_name="Роль",
        max_length=32,
        choices=ROLE_CHOICES,
        default="user",
    )

    @property
    def is_user(self):
        return self.role == User.USER_ROLE

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR_ROLE

    @property
    def is_admin(self):
        return self.role == User.ADMIN_ROLE
