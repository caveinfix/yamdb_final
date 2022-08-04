from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_year


class CustomUser(AbstractUser):
    """Кастомная модель пользователя. Добавлены поля биографии и роли."""

    ROLE_CHOICES = (
        ("user", "Аутентифицированный пользователь"),
        ("moderator", "Модератор"),
        ("admin", "Администратор"),
    )
    email = models.EmailField(
        "Электронная почта",
        unique=True
    )
    confirmation_code = models.CharField(
        "Код подтверждения",
        blank=True,
        max_length=32
    )
    bio = models.TextField(
        "О себе",
        blank=True,
        null=True
    )
    role = models.CharField(
        "Пользовательская роль",
        choices=ROLE_CHOICES,
        default="user",
        max_length=255
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == "user"

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_admin(self):
        return self.role == "admin"


class Category(models.Model):
    name = models.CharField(
        "Название категории",
        max_length=256,
        db_index=True,
    )
    slug = models.SlugField(
        "Slug",
        unique=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        "Название жанра",
        max_length=256,
        db_index=True,
    )
    slug = models.SlugField(
        "Slug",
        unique=True,
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        "Название произведения",
        max_length=256,
    )
    year = models.PositiveSmallIntegerField(
        "Год произведения",
        validators=[validate_year],
        db_index=True,
    )
    description = models.TextField(
        "Описание произведения",
        max_length=200,
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="titles",
        verbose_name="Жанр произведения",
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория произведения",
    )
    rating = models.IntegerField(
        "Рейтинг произведения",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор отзыва",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
    )
    text = models.TextField(
        "Текст отзыва",
    )
    score = models.IntegerField(
        "Оценка",
        validators=[MaxValueValidator(10), MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_author_title",
                fields=("author", "title",),
            )
        ]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    text = models.TextField(
        "Текст комментария",
    )
    pub_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text
