from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    raw_id_fields = ('genre',)
    list_display = (
        'pk',
        'name',
        'category',
        'year',
        'description',
    )
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title_id',
        'text',
        'score',
        'pub_date',
        'author',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'review_id',
        'text',
        'pub_date',
        'author',
    )
    search_fields = ('text',)
