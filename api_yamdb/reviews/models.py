from typing import Tuple

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

from .validators import validate_correct_year

REVIEW_ORDERING: Tuple[str] = ("-pub_date",)
COMMENT_ORDERING: Tuple[str] = ("-pub_date",)


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Строка идентификатор категории',
        unique=True,
        max_length=50,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Строка идентификатор жанра',
        unique=True,
        max_length=50,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=256,
    )
    year = models.IntegerField(
        verbose_name='Год создания произведения',
        validators=[validate_correct_year]
    )
    descriptions = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
        null=True
    )
    genre = models.ForeignKey(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title_id = models.ForeignKey(
        Title,
        related_name='reviews',
        verbose_name='Произведение',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст ревью',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    score = models.IntegerField(
        default=10, validators=[MaxValueValidator(10), MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = REVIEW_ORDERING
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'


class Comment(models.Model):
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Ревью'
    )
    text = models.TextField(
        verbose_name="Текст Комментария",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = COMMENT_ORDERING
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
