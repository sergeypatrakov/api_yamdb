from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genre
        lookup_field = 'slug'


class GetTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(
        many=True,
    )
    category = CategorySerializer(
    )

    class Meta:
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")
        model = Title

    def get_rating(self, obj):
        if not Review.objects.filter(title_id=obj.id):
            return None
        return Review.objects.aggregate(Avg('score'))


class PostPutPatchDeleteTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        for genre in genres:
            TitleGenre.objects.create(
                genre=genre,
                title=title
            )

        return title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        many=False,
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id')
        )
        author = self.context['request'].user
        if Review.objects.filter(title_id=title, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв'
            )
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
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
        max_length=254,
        required=True,
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя'
            )
        duplicated_username = User.objects.filter(
            username=username
        ).exists()
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
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
        max_length=254,
        required=True,
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150
    )

    def validate_username(self, username):
        return UserSerializer.validate_username(self, username)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
