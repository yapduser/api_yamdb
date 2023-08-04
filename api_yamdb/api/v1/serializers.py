from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CurrentUserDefault,
    CharField,
    EmailField,
    IntegerField,
)
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, Serializer

from reviews.models import Category, Comment, Genre, Title, Review, User
from reviews.validators import username_validator


class GenreSerializer(ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ("id",)


class CategorySerializer(ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        exclude = ("id",)


class TitleSerializer(ModelSerializer):
    """Базовый сериализатор произведений."""

    class Meta:
        model = Title
        fields = "__all__"


class TitleGetSerializer(TitleSerializer):
    """Сериализатор для получения произведений."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = IntegerField()

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


class TitleWriteSerializer(TitleSerializer):
    """Сериализатор для изменения произведений."""

    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field="slug",
        many=True,
    )


class AuthorSerializer(ModelSerializer):
    """Базовый сериализатор поля author."""

    author = SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=CurrentUserDefault(),
    )

    class Meta:
        fields = "__all__"


class ReviewSerializer(AuthorSerializer):
    """Сериализатор для отзывов."""

    def validate(self, data):
        request = self.context.get("request")
        if request.method != "POST":
            return data
        title = get_object_or_404(
            Title, pk=self.context["view"].kwargs.get("title_id")
        )
        if title.reviews.filter(author=request.user).exists():
            raise ValidationError(
                "Можно оставить только один отзыв на произведение!"
            )
        return data

    class Meta(AuthorSerializer.Meta):
        model = Review
        read_only_fields = ("title",)


class CommentSerializer(AuthorSerializer):
    """Сериализатор для комментариев."""

    class Meta(AuthorSerializer.Meta):
        model = Comment
        read_only_fields = ("review",)


class SignUpSerializer(Serializer):
    """Сериализатор регистрации пользователя."""

    username = CharField(
        max_length=settings.LENGTH_L,
        required=True,
        validators=[username_validator],
    )
    email = EmailField(
        max_length=settings.LENGTH_XL,
        required=True,
    )

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        user_data = User.objects.filter(username=username, email=email)
        if not user_data.exists():
            if User.objects.filter(username=username):
                raise ValidationError(
                    "Пользователь с таким username существует"
                )
            if User.objects.filter(email=email):
                raise ValidationError("Пользователь с таким email существует")
        return attrs


class GetTokenSerializer(Serializer):
    """Сериализатор получения токена."""

    username = CharField(
        max_length=settings.LENGTH_L,
        required=True,
    )
    confirmation_code = CharField(
        required=True,
    )


class AdminUserSerializer(ModelSerializer):
    """Сериализатор администрирования пользователей."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserSerializer(AdminUserSerializer):
    """Сериализатор редактирования профиля пользователя."""

    class Meta(AdminUserSerializer.Meta):
        read_only_fields = ("role",)
