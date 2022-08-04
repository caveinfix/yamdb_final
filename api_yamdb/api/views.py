from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    UserSerializer,
)
from .mixins import ListCreateDestroyViewSet
from .tokens import get_jwt_token
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminOrSuperuser,
    ProfilePermission,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModerator,
    IsAuthorizedOrReadOnly,
)
from .filters import TitleFilter


class SignupViewSet(CreateAPIView):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, partial=False)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(request.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_jwt_token(request):
    username = request.data.get("username")
    if not request.data or not username:
        raise ParseError
    user = get_object_or_404(
        CustomUser,
        username=username,
    )
    if user.confirmation_code != request.data.get("confirmation_code"):
        raise ValidationError(code=400)
    return Response(get_jwt_token(user), status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = "username"

    def get_permissions(self):
        if self.kwargs.get("username") == "me":
            return (ProfilePermission(),)
        else:
            return (IsAdminOrSuperuser(),)

    def perform_create(self, serializer):
        if not serializer.validated_data.get("role"):
            serializer.validated_data["role"] = "user"
        return serializer.save()

    def get_object(self):
        if self.kwargs.get("username") == "me":
            user = CustomUser.objects.get(pk=self.request.user.pk)
            return self.serializer_class(user).data
        return super(UserViewSet, self).get_object()

    def partial_update(self, request, *args, **kwargs):
        if self.kwargs.get("username") == "me":
            user = CustomUser.objects.get(pk=self.request.user.pk)
            serializer = self.serializer_class(
                user, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                if request.user.is_user:  # user не может изменить роль
                    serializer.validated_data["role"] = "user"
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super(UserViewSet, self).partial_update(request)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ("POST", "PATCH"):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorizedOrReadOnly,)

    def get_permissions(self):
        if (self.action == "update") or (self.action == "destroy"):
            permission_classes = [IsAuthorOrAdminOrModerator]
        else:
            permission_classes = [IsAuthorizedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        new_queryset = Review.objects.filter(title=title_id)
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        if Review.objects.filter(
            title=title, author=self.request.user
        ).exists():
            raise ValidationError(code=400)
        serializer.save(
            author=self.request.user,
            title=title,
        )
        rating = Review.objects.filter(title=title).aggregate(Avg("score"))
        title.rating = rating["score__avg"]
        title.save(update_fields=["rating"])

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Изменение чужих постов запрещено!")
        serializer.save()
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        rating = Review.objects.filter(title=title).aggregate(Avg("score"))
        title.rating = rating["score__avg"]
        title.save(update_fields=["rating"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        rating = Review.objects.filter(title=title).aggregate(Avg("score"))
        title.rating = rating["score__avg"]
        title.save(update_fields=["rating"])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorizedOrReadOnly,)

    def get_permissions(self):
        if (self.action == "update") or (self.action == "destroy"):
            permission_classes = [IsAuthorOrAdminOrModerator]
        else:
            permission_classes = [IsAuthorizedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        new_queryset = Comment.objects.filter(review=review_id)
        return new_queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        serializer.save(
            author=self.request.user,
            review=review,
        )

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Изменение чужих постов запрещено!")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
