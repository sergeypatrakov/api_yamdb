from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api_yamdb import settings
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Genre
        lookup_field = 'slug'


class GetTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(
        many=True,
    )
    category = CategorySerializer()

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class PostPutPatchDeleteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        titlegenre_objects = (TitleGenre(genre=genre, title=title)
                              for genre in genres)

        TitleGenre.objects.bulk_create(titlegenre_objects)

        return title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='id', many=False, read_only=True)

    class Meta:
        model = Review
        fields = ('title', 'text', 'author', 'score', 'pub_date', 'id')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id'))
        author = self.context['request'].user
        if Review.objects.filter(title_id=title, author=author).exists():
            raise serializers.ValidationError('Вы уже оставляли отзыв')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    review = serializers.SlugRelatedField(
        slug_field='text',
        many=False,
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('review', 'text', 'author', 'pub_date', 'id')


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
        max_length=254,
        required=True,
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        duplicated_username = User.objects.filter(username=username).exists()
        if duplicated_username:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        return username

    def nonadmin_update(self, instance, validated_data):
        validated_data.pop('role', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.RegexField(
        regex=settings.ALLOWED_USERNAME_RE,
        max_length=150
    )

    def create(self, validated_data):
        try:
            user = User.objects.get(username=validated_data['username'])
        except User.DoesNotExist:
            user = User.objects.create_user(**validated_data)
        return user

    def validate(self, data):

        if data.get('email') and data.get('username'):
            if (
                User.objects.filter(email=data['email']).exists()
                and not User.objects.filter(username=data['username']).exists()
            ):
                raise serializers.ValidationError(
                    'Недопустимая комбинация username и email.'
                )
            if User.objects.filter(username=data["username"]).exists() and (
                User.objects.get(
                    username=data['username']).email != data['email']
            ):
                raise serializers.ValidationError(
                    'Email не соответсвует пользователю.')
        return data

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return username


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
