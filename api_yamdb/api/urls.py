from django.urls import include, path
from rest_framework import routers

from .views import (
    TitleViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupViewSet,
    UserViewSet,
    create_jwt_token,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename='users')
router.register(r"genres", GenreViewSet, basename='genres')
router.register(r"categories", CategoryViewSet, basename='categories')
router.register(r"titles", TitleViewSet, basename='titles')
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename='reviews'
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename='comments',
)


urlpatterns = [
    path("v1/auth/signup/", SignupViewSet.as_view()),
    path("v1/auth/token/", create_jwt_token),
    path("v1/", include(router.urls)),
]
