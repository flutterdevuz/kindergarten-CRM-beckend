from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .serializers import KindergartenLoginSerializer, StaffLoginSerializer, ParentLoginSerializer

class KindergartenLoginView(TokenObtainPairView):
    """
    Bog'cha adminlari uchun tizimga kirish (Login) endpointi.
    Faol (active) bog'cha admini bo'lsa JWT tokenlar qaytaradi.
    """
    serializer_class = KindergartenLoginSerializer


class StaffLoginView(TokenObtainPairView):
    """
    Bog'cha xodimlari uchun tizimga kirish (Login) endpointi.
    `kinder_id` (bog'cha ID) ni ham qabul qiladi.
    """
    serializer_class = StaffLoginSerializer


class ParentLoginView(TokenObtainPairView):
    """
    Ota-onalar uchun tizimga kirish (Login) endpointi.
    `kinder_id` (bog'cha ID) ni ham qabul qiladi.
    """
    serializer_class = ParentLoginSerializer


from rest_framework import generics, permissions
from .models import ParentProfile
from .parent_serializers import ParentProfileSerializer

class BaseParentAPIView:
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
            return ParentProfile.objects.filter(kindergarten=kindergarten)
        return ParentProfile.objects.none()

class ParentListAPIView(BaseParentAPIView, generics.ListAPIView):
    serializer_class = ParentProfileSerializer

class ParentCreateAPIView(BaseParentAPIView, generics.CreateAPIView):
    serializer_class = ParentProfileSerializer

    def perform_create(self, serializer):
        kindergarten = self.get_kindergarten()
        serializer.save(kindergarten=kindergarten)

class ParentRetrieveAPIView(BaseParentAPIView, generics.RetrieveAPIView):
    serializer_class = ParentProfileSerializer

class ParentUpdateAPIView(BaseParentAPIView, generics.UpdateAPIView):
    serializer_class = ParentProfileSerializer

class ParentDeleteAPIView(BaseParentAPIView, generics.DestroyAPIView):
    serializer_class = ParentProfileSerializer

# ── Roles Views ──
from .models import KindergartenRole, StaffProfile
from .staff_serializers import KindergartenRoleSerializer, StaffProfileSerializer

class BaseRoleAPIView:
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
            return KindergartenRole.objects.filter(kindergarten=kindergarten)
        return KindergartenRole.objects.none()

class RoleListAPIView(BaseRoleAPIView, generics.ListAPIView):
    serializer_class = KindergartenRoleSerializer

class RoleCreateAPIView(BaseRoleAPIView, generics.CreateAPIView):
    serializer_class = KindergartenRoleSerializer
    def perform_create(self, serializer):
        serializer.save(kindergarten=self.get_kindergarten())

class RoleRetrieveAPIView(BaseRoleAPIView, generics.RetrieveAPIView):
    serializer_class = KindergartenRoleSerializer

class RoleUpdateAPIView(BaseRoleAPIView, generics.UpdateAPIView):
    serializer_class = KindergartenRoleSerializer

class RoleDeleteAPIView(BaseRoleAPIView, generics.DestroyAPIView):
    serializer_class = KindergartenRoleSerializer


# ── Staff Views ──
class BaseStaffAPIView:
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
            return StaffProfile.objects.filter(kindergarten=kindergarten)
        return StaffProfile.objects.none()

class StaffListAPIView(BaseStaffAPIView, generics.ListAPIView):
    serializer_class = StaffProfileSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(groups=group_id)
        return qs

class StaffCreateAPIView(BaseStaffAPIView, generics.CreateAPIView):
    serializer_class = StaffProfileSerializer
    def perform_create(self, serializer):
        serializer.save(kindergarten=self.get_kindergarten())

class StaffRetrieveAPIView(BaseStaffAPIView, generics.RetrieveAPIView):
    serializer_class = StaffProfileSerializer

class StaffUpdateAPIView(BaseStaffAPIView, generics.UpdateAPIView):
    serializer_class = StaffProfileSerializer

class StaffDeleteAPIView(BaseStaffAPIView, generics.DestroyAPIView):
    serializer_class = StaffProfileSerializer
