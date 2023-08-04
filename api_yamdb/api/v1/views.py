from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.v1 import permissions as pm
from api.v1 import serializers as sl
from api.v1.filters import TitleFilter
from api.v1.mixins import GenreCategoryMixin
from reviews.models import Title, Genre, Category, Review, User


class TitleViewSet(viewsets.ModelViewSet):
    """Управление произведениями.

    Позволяет просматривать, создавать, обновлять и удалять произведения.
    Для пользователей с правами администратора разрешены все операции,
    остальные пользователи могут только просматривать данные.
    """

    serializer_class = sl.TitleGetSerializer
    permission_classes = (pm.IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.annotate(rating=Avg("reviews__score")).order_by(
            "id"
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return sl.TitleGetSerializer
        return sl.TitleWriteSerializer


class GenreViewSet(GenreCategoryMixin):
    """Управление жанрами.

    Позволяет просматривать, создавать и удалять жанры.
    Для пользователей с правами администратора разрешены все операции,
    остальные пользователи могут только просматривать данные.
    """

    queryset = Genre.objects.all()
    serializer_class = sl.GenreSerializer
    filter_backends = (SearchFilter,)


class CategoriesViewSet(GenreCategoryMixin):
    """Управление категориями.

    Позволяет просматривать, создавать и удалять категории.
    Для пользователей с правами администратора разрешены все операции,
    остальные пользователи могут только просматривать данные.
    """

    queryset = Category.objects.all()
    serializer_class = sl.CategorySerializer
    filter_backends = (SearchFilter,)


class ReviewViewSet(viewsets.ModelViewSet):
    """Управление отзывами.

    Позволяет просматривать, создавать, обновлять и удалять отзывы.
    Отзывы могут быть созданы, изменены или удалены только их автором,
    а также администратором или модератором.
    Все пользователи могут просматривать отзывы, но не могут изменять или
    удалять чужие отзывы.
    """

    serializer_class = sl.ReviewSerializer
    permission_classes = (pm.IsAuthorModeratorAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Управление комментариями.

    Позволяет просматривать, создавать, обновлять и удалять комментарии.
    Комментарии могут быть созданы, изменены или удалены только их автором,
    а также администратором или модератором.
    Все пользователи могут просматривать комментарии, но не могут изменять или
    удалять чужие комментарии.
    """

    serializer_class = sl.CommentSerializer
    permission_classes = (pm.IsAuthorModeratorAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all().select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    """Управление данными пользователей.

    Класс представления для работы с данными пользователей.
    Позволяет просматривать, создавать, обновлять и удалять пользователей.
    """

    queryset = User.objects.all()
    serializer_class = sl.AdminUserSerializer
    permission_classes = (pm.IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ("get", "post", "delete", "patch")

    @action(
        detail=False,
        methods=("get", "patch"),
        permission_classes=(IsAuthenticated,),
        url_path=settings.USER_READ_EDIT_URL,
    )
    def user_read_edit(self, request):
        """Чтение и редактирование данных пользователя.

        Параметры:
            - request: Запрос, с данными для редактирования пользователя.

        Возвращает:
            - response: Ответ с данными пользователя в случае успешного
            чтения или редактирования.

        Исключения:
            - Http400: Данные для редактирования некорректны.
        """
        serializer = sl.UserSerializer(
            request.user, partial=True, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "PATCH":
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSignUp(APIView):
    """Создать пользователя.

    Зарегистрировать нового пользователя и отправить email сообщение с кодом
    подтверждения.
    """

    @staticmethod
    def send_code(email, confirmation_code):
        """Отправить email с кодом подтверждения на указанный адрес.

        Параметры:
            - email: Адрес пользователя.
            - confirmation_code: Код подтверждения, который будет отправлен.

        Возвращает:
            - None
        """
        send_mail(
            subject="Код подтверждения",
            message=f"Код для подтверждения регистрации: {confirmation_code}",
            from_email=settings.EMAIL_YAMDB,
            recipient_list=[email],
            fail_silently=True,
        )

    def post(self, request):
        """Зарегистрировать нового пользователя.

        Параметры:
            - request: Запрос с данными пользователя для регистрации.

        Возвращает:
            - response: Ответ с данными пользователя в случае успешной
            регистрации.

        Исключения:
            - Http400: Данные, отправленные в запросе, некорректны.
        """
        serializer = sl.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        self.send_code(user.email, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGetToken(APIView):
    """Получить JWT токен."""

    def post(self, request):
        """Создать JWT токен.

        Параметры:
            - request: Запрос, c данными для аутентификации
            (username и confirmation_code).

        Возвращает:
            - response: Ответ с токеном в случае успешной аутентификации или
            сообщение об ошибке.

        Исключения:
            - Http404: Пользователь с указанным username не найден.
            - Http400: Код подтверждения неверный.
        """
        serializer = sl.GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username, confirmation_code = serializer.validated_data.values()
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            msg = {"confirmation_code": "Код подтверждения неверный"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"token": str(AccessToken.for_user(user))}
        return Response(msg, status=status.HTTP_200_OK)
