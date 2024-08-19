from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from user_service.serializers import UserCreateSerializer, UserUpdateSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserCreateSerializer

    @extend_schema(
        summary="register new user",
        responses={200: UserCreateSerializer(many=False)}
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UpdateRetrieveUserView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="retrieve your profile",
        responses={200: UserUpdateSerializer(many=False)}
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="update your profile",
        responses={200: UserUpdateSerializer(many=False)}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="partial update your profile",
        responses={200: UserUpdateSerializer(many=False)}
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
