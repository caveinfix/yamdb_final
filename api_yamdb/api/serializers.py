from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    validators = [
        UniqueTogetherValidator(
            queryset=CustomUser.objects.all(), fields=["username", "email"]
        )
    ]

    def create(self, validated_data):
        confirmation_code = get_random_string(length=32)  # generate code
        username = validated_data["username"]
        role = validated_data.get("role", "user")  # default - user
        if username == "me":
            raise ValidationError(code=400)
        email = str(validated_data["email"])
        user = CustomUser(
            username=username,
            email=email,
            confirmation_code=confirmation_code,
            role=role
        )
        current_user_admin = False
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            current_user_admin = request.user.is_admin
        if not current_user_admin:  # отправка, если не админ
            send_mail(
                "Код подтверждения для регистрации YamDB",
                f"{username} Ваш код подтверждения: {confirmation_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=(email,),
            )
        user.save()
        return validated_data


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            "name",
            "slug",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для GET."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        # read_only_fields = ("id",)


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для POST, PATH."""

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.HiddenField(
        default=serializers.PrimaryKeyRelatedField(read_only=True),
    )

    class Meta:
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(), fields=["author", "title"]
            )
        ]
        fields = ("id", "text", "author", "score", "pub_date", "title")
        read_only_fields = ("id", "author", "pub_date", "title")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    review = serializers.HiddenField(
        default=serializers.PrimaryKeyRelatedField(read_only=True),
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date", "review")
        read_only_fields = ("id", "author", "pub_date", "review")
