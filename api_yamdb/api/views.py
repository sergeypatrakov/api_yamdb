from http import HTTPStatus

from django import db
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.filters import GenreFilter
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetCodeSerializer,
                          GetTitleSerializer, GetTokenSerializer,
                          PostPutPatchDeleteTitleSerializer, ReviewSerializer,
                          UserSerializer)
from .utils import send_confirmation_mail
from .viewsets import CreateListDeleteViewSet


class CategoryViewSet(CreateListDeleteViewSet):
    """Вьюсет категорий произведений."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CreateListDeleteViewSet):
    """Вьюсет жанров произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведений."""
    queryset = Title.objects.annotate(rating=db.models.Avg("reviews__score"))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GenreFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return GetTitleSerializer
        return PostPutPatchDeleteTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет ревью."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    filter_backends = (filters.SearchFilter,)
    lookup_field = "username"
    search_fields = ("username",)
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        ["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
        detail=False,
        url_path="me",
    )
    def user_selfview(self, request):
        """Вьюфункция собвственного профиля."""
        if not request.data:
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=HTTPStatus.OK)
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if request.user.is_admin:
            serializer.update(request.user, serializer.validated_data)
        else:
            serializer.nonadmin_update(request.user, serializer.validated_data)

        return Response(serializer.data, status=HTTPStatus.OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    """Вью регистрации и входа."""
    serializer = GetCodeSerializer(data=request.data)

    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    user = serializer.save()
    confirmation_code = send_confirmation_mail(user)
    User.objects.filter(username=user.username).update(
        confirmation_code=confirmation_code
    )

    return Response(request.data, status=HTTPStatus.OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def token_view(request):
    """Вью токена работы с API по коду подтверждения."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get("username")
    confirmation_code = serializer.validated_data.get("confirmation_code")
    user = get_object_or_404(User, username=username)

    if confirmation_code == user.confirmation_code:
        token = AccessToken.for_user(user)

        return Response({"token": f"{token}"}, status=HTTPStatus.OK)

    return Response(
        {"confirmation_code": "Неверный код подтверждения"},
        status=HTTPStatus.BAD_REQUEST,
    )
