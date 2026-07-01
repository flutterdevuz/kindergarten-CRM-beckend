from rest_framework import generics, permissions
from .models import Child
from .serializers import ChildSerializer

class BaseKindergartenAPIView:
    """Base class to automatically filter by the admin's kindergarten."""
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
            return Child.objects.filter(kindergarten=kindergarten)
        return Child.objects.none()

class ChildListAPIView(BaseKindergartenAPIView, generics.ListAPIView):
    serializer_class = ChildSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(group=group_id)
        return qs

class ChildCreateAPIView(BaseKindergartenAPIView, generics.CreateAPIView):
    serializer_class = ChildSerializer

    def perform_create(self, serializer):
        kindergarten = self.get_kindergarten()
        serializer.save(kindergarten=kindergarten)

class ChildRetrieveAPIView(BaseKindergartenAPIView, generics.RetrieveAPIView):
    serializer_class = ChildSerializer


class ChildUpdateAPIView(BaseKindergartenAPIView, generics.UpdateAPIView):
    serializer_class = ChildSerializer

class ChildDeleteAPIView(BaseKindergartenAPIView, generics.DestroyAPIView):
    serializer_class = ChildSerializer
