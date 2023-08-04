from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import username_validator

SCORE_MIN = 1
SCORE_MAX = 10
ROLES = {
    "user": "user",
    "admin": "admin",
    "moderator": "moderator",
}
USER = ROLES["user"]
ADMIN = ROLES["admin"]
MODERATOR = ROLES["moderator"]


def get_current_year():
    return timezone.now().year


class User(AbstractUser):
    """Модель пользователя."""

    roles = [*ROLES.items()]

    username = models.CharField(
        verbose_name="username",
        max_length=settings.LENGTH_L,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        verbose_name="email",
        max_length=settings.LENGTH_XL,
        unique=True,
    )
    bio = models.TextField(
        verbose_name="Биография",
        blank=True,
    )
    role = models.CharField(
        verbose_name="Роль",
        max_length=len(max(ROLES.values(), key=len)),
        choices=roles,
        default=USER,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser


class InfoModel(models.Model):
    """Абстрактная модель."""

    name = models.CharField(
        verbose_name="Название",
        max_length=settings.LENGTH_XXL,
        db_index=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        max_length=settings.LENGTH_M,
        unique=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Genre(InfoModel):
    """Модель жанра."""

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        default_related_name = "genres"


class Category(InfoModel):
    """Модель категории."""

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        default_related_name = "categories"


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        verbose_name="Название",
        max_length=settings.LENGTH_XXL,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год создания",
        db_index=True,
        validators=[MaxValueValidator(get_current_year)],
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.genre} {self.title}"


class BaseAuthorModel(models.Model):
    """Абстрактная модель.

    Добавляет к модели автора, текст и дату публикации.
    """

    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text


class Review(BaseAuthorModel):
    """Модель отзывов на произведения."""

    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        validators=[
            MinValueValidator(
                SCORE_MIN,
                message=f"Нельзя поставить оценку ниже {SCORE_MIN}.",
            ),
            MaxValueValidator(
                SCORE_MAX,
                message=f"Нельзя поставить оценку выше {SCORE_MAX}.",
            ),
        ],
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"],
                name="unique_author_title",
            ),
        )


class Comment(BaseAuthorModel):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
