from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (CustomTokenObtainPairSerializer, LogoutSerializer, PublicUserSerializer, RegisterSerializer,
                          UpdateUserSerializer,
                          UserSerializer)


@extend_schema(
        summary="Регистрация пользователя",
        description=(
                "Создаёт нового пользователя. Если поле `username` не передано или пустое — оно будет "
                "сгенерировано автоматически функцией `generate_username_from_names` (по name/last_name).\n\n"
                "Пароль должен быть не короче 8 символов. Поле `email` обязательно и должно быть уникальным."
        ),
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                    response=UserSerializer,
                    description="Пользователь успешно создан — возвращаются данные пользователя.",
                    examples=[
                        OpenApiExample(
                                name="Пример",
                                value={
                                    "id": 1,
                                    "username": "ivanov",
                                    "email": "ivan@example.com",
                                    "first_name": "Ivan",
                                    "last_name": "Ivanov",
                                    "is_staff": False,
                                    "is_superuser": False,
                                    "profile": {"image_url": None},
                                },
                        )
                    ],
            ),
            400: OpenApiResponse(description="Ошибка валидации: неверные поля (например, email уже занят)."),
            500: OpenApiResponse(description="Внутренняя ошибка сервера."),
        },
)
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []


class UserMeView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method and self.request.method.lower() == "patch":
            return UpdateUserSerializer
        return UserSerializer

    @extend_schema(
            summary="Информация о текущем пользователе",
            description="Возвращает данные текущего аутентифицированного пользователя.",
            responses={
                200: OpenApiResponse(
                        response=UserSerializer,
                        description="Данные текущего пользователя.",
                        examples=[
                            OpenApiExample(
                                    "Пример",
                                    value={
                                        "id": 1,
                                        "username": "timur",
                                        "email": "timur@example.com",
                                        "first_name": "Timur",
                                        "last_name": "S.",
                                        "is_staff": False,
                                        "is_superuser": False,
                                        "profile": {"image_url": "https://.../avatars/1.png"},
                                    },
                            )
                        ],
                ),
                401: OpenApiResponse(description="Unauthorized"),
                500: OpenApiResponse(description="Внутренняя ошибка сервера."),
            },
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(UserSerializer(instance, context={"request": request}).data)

    @extend_schema(
            summary="Обновление пользователя (частично)",
            description=(
                    "Частичное обновление полей пользователя: `first_name`, `last_name` и загрузка `photo`.\n\n"
                    "Отправлять как `multipart/form-data` (файл в поле `photo`). Если MinIO/S3 недоступен, "
                    "сохранение изображения будет залогировано, но остальные изменения применятся."
            ),
            request=UpdateUserSerializer,
            examples=[
                OpenApiExample(
                        name="Только имя/фамилия (form-data)",
                        value={"first_name": "Ivan", "last_name": "Ivanov"},
                        request_only=True,
                        media_type="multipart/form-data",
                ),
                OpenApiExample(
                        name="С загрузкой фото (form-data)",
                        value={"first_name": "Ivan", "photo": "(binary file) avatar.png"},
                        request_only=True,
                        media_type="multipart/form-data",
                ),
            ],
            responses={
                200: OpenApiResponse(
                        response=PublicUserSerializer,
                        description="Обновлённый пользователь",
                        examples=[
                            OpenApiExample(
                                    name="Пример успешного ответа",
                                    value={
                                        "username": "ivan",
                                        "email": "ivan@example.com",
                                        "first_name": "Ivan",
                                        "last_name": "Ivanov",
                                        "profile": {"image_url": "https://minio.example.com/avatars/123.png"},
                                    },
                                    response_only=True,
                                    media_type="application/json",
                            )
                        ],
                ),
                400: OpenApiResponse(description="Ошибка валидации"),
                401: OpenApiResponse(description="Unauthorized"),
                500: OpenApiResponse(description="Внутренняя ошибка сервера."),
            },
    )
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(PublicUserSerializer(instance, context={"request": request}).data)


@extend_schema(
        summary="Вход — получение пары JWT (refresh / access) и данных пользователя",
        description=(
                "Аутентификация по username + password. В ответе возвращается `{refresh, access}` и поле `user` — "
                "сериализованные данные пользователя (`UserSerializer`)."
        ),
        request=TokenObtainPairSerializer,
        responses={
            200: OpenApiResponse(
                    response=CustomTokenObtainPairSerializer,
                    description="Успешный логин. Возвращает токены и объект user.",
                    examples=[
                        OpenApiExample(
                                name="Пример успешного ответа",
                                value={
                                    "refresh": "<refresh_token>",
                                    "access": "<access_token>",
                                    "user": {
                                        "id": 1,
                                        "username": "timur",
                                        "email": "timur@example.com",
                                        "first_name": "Timur",
                                        "last_name": "S.",
                                        "is_staff": False,
                                        "is_superuser": False,
                                        "profile": {"image_url": None},
                                    },
                                },
                        )
                    ],
            ),
            401: OpenApiResponse(description="Неверные учётные данные"),
            400: OpenApiResponse(description="Неверный формат запроса"),
            500: OpenApiResponse(description="Внутренняя ошибка сервера."),
        },
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []


class LogoutAndBlacklistRefreshTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
            summary="Logout — добавление refresh токена в `blacklist`",
            description=(
                    "Полагает `refresh-token` в blacklist (используется simplejwt + blacklist app). "
                    "Требуется действительный `access-token` в заголовке Authorization."
            ),
            request=LogoutSerializer,
            responses={
                205: OpenApiResponse(description="Токен успешно занесён в blacklist (Reset Content)."),
                400: OpenApiResponse(
                        description="Некорректный/отсутствующий refresh токен.",
                        examples=[
                            OpenApiExample(
                                    name="Токен отсутствует",
                                    value={"message": "Refresh token is required"}
                            ),
                            OpenApiExample(
                                    name="Неверный или просроченный токен",
                                    value={"message": "Invalid or expired token. Error details: <error text>"}
                            ),
                        ],
                ),
                401: OpenApiResponse(description="Unauthorized: недостаточно прав (требуется access token)."),
                500: OpenApiResponse(description="Внутренняя ошибка сервера."),
            },
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": f"Invalid or expired token. Error details: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(generics.UpdateAPIView):
    """
    PATCH/PUT endpoint для обновления current user.
    Принимает multipart/form-data (photo file).
    """
    serializer_class = UpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)  # для file upload

    def get_object(self):
        return self.request.user
