from user_service.serializers import UserCreateSerializer, UserUpdateSerializer

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView


class CreateUserView(CreateAPIView):
    serializer_class = UserCreateSerializer


class UpdateRetrieveUserView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user
