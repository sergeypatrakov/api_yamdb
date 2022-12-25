from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, signup_view,
                    token_view)

router = routers.DefaultRouter()

router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet)
router.register("users", UserViewSet)
router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewViewSet,
    basename="title_id")
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="review_id",
)

urlpatterns = [
    path("v1/auth/signup/", signup_view, name="signup"),
    path("v1/auth/token/", token_view, name="token"),
    path("v1/", include(router.urls)),
]
