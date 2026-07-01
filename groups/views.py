from rest_framework import generics, permissions
from .models import Group, Camera
from .serializers import GroupSerializer, CameraSerializer

class BaseGroupAPIView:
    permission_classes = [permissions.IsAuthenticated]

    def get_kindergarten(self):
        user = self.request.user
        if user.role == 'admin':
            return user.admin_profile.kindergarten
        elif user.role == 'staff':
            return user.staff_profile.kindergarten
        return None

    def get_queryset(self):
        kindergarten = self.get_kindergarten()
        if kindergarten:
            return Group.objects.filter(kindergarten=kindergarten)
        return Group.objects.none()

class GroupListAPIView(BaseGroupAPIView, generics.ListAPIView):
    serializer_class = GroupSerializer

class GroupCreateAPIView(BaseGroupAPIView, generics.CreateAPIView):
    serializer_class = GroupSerializer

    def perform_create(self, serializer):
        kindergarten = self.get_kindergarten()
        serializer.save(kindergarten=kindergarten)

class GroupRetrieveAPIView(BaseGroupAPIView, generics.RetrieveAPIView):
    serializer_class = GroupSerializer

class GroupUpdateAPIView(BaseGroupAPIView, generics.UpdateAPIView):
    serializer_class = GroupSerializer

class GroupDeleteAPIView(BaseGroupAPIView, generics.DestroyAPIView):
    serializer_class = GroupSerializer

class BaseCameraAPIView:
    permission_classes = [permissions.IsAuthenticated]

    def get_kindergarten(self):
        user = self.request.user
        if user.role == 'admin':
            return user.admin_profile.kindergarten
        elif user.role == 'staff':
            return user.staff_profile.kindergarten
        return None

    def get_queryset(self):
        kindergarten = self.get_kindergarten()
        if kindergarten:
            return Camera.objects.filter(kindergarten=kindergarten)
        return Camera.objects.none()

class CameraListAPIView(BaseCameraAPIView, generics.ListAPIView):
    serializer_class = CameraSerializer

class CameraCreateAPIView(BaseCameraAPIView, generics.CreateAPIView):
    serializer_class = CameraSerializer

    def perform_create(self, serializer):
        kindergarten = self.get_kindergarten()
        serializer.save(kindergarten=kindergarten)

class CameraRetrieveAPIView(BaseCameraAPIView, generics.RetrieveAPIView):
    serializer_class = CameraSerializer

class CameraUpdateAPIView(BaseCameraAPIView, generics.UpdateAPIView):
    serializer_class = CameraSerializer

class CameraDeleteAPIView(BaseCameraAPIView, generics.DestroyAPIView):
    serializer_class = CameraSerializer
