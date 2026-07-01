from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import ChildAttendance
from .serializers import ChildAttendanceSerializer, BulkAttendanceSerializer
from children.models import Child
from groups.models import Group

class BaseAttendanceAPIView:
    permission_classes = [permissions.IsAuthenticated]

    def get_kindergarten(self):
        user = self.request.user
        if user.role == 'admin':
            return user.admin_profile.kindergarten
        elif user.role == 'staff':
            return user.staff_profile.kindergarten
        return None

class AttendanceListAPIView(BaseAttendanceAPIView, generics.ListAPIView):
    """
    Davomatlar ro'yxatini olish. 
    Query orqali filtrlash mumkin: ?group_id=...&date=YYYY-MM-DD
    """
    serializer_class = ChildAttendanceSerializer

    def get_queryset(self):
        kindergarten = self.get_kindergarten()
        if not kindergarten:
            return ChildAttendance.objects.none()
            
        queryset = ChildAttendance.objects.filter(kindergarten=kindergarten)
        
        group_id = self.request.query_params.get('group_id')
        date = self.request.query_params.get('date')
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset

class BulkAttendanceMarkAPIView(BaseAttendanceAPIView, generics.GenericAPIView):
    """
    Bitta butun guruh uchun davomatni bittada saqlash (Bulk Mark)
    """
    serializer_class = BulkAttendanceSerializer

    def post(self, request, *args, **kwargs):
        kindergarten = self.get_kindergarten()
        if not kindergarten:
            return Response({"error": "Sizda ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

        serializer = BulkAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            group_id = serializer.validated_data['group_id']
            date_val = serializer.validated_data['date']
            records = serializer.validated_data['records']

            # Guruh tekshiruvi
            try:
                group = Group.objects.get(id=group_id, kindergarten=kindergarten)
            except Group.DoesNotExist:
                return Response({"error": "Guruh topilmadi yoki bu bog'chaga tegishli emas."}, status=status.HTTP_404_NOT_FOUND)

            created_or_updated = []
            for record in records:
                child_id = record.get('child_id')
                status_val = record.get('status', 'present')
                time_in = record.get('time_in')
                time_out = record.get('time_out')

                try:
                    child = Child.objects.get(id=child_id, group=group, kindergarten=kindergarten)
                except Child.DoesNotExist:
                    continue # Bola topilmasa o'tkazib yuboramiz

                # Update or create attendance
                obj, created = ChildAttendance.objects.update_or_create(
                    child=child,
                    date=date_val,
                    defaults={
                        'group': group,
                        'kindergarten': kindergarten,
                        'status': status_val,
                        'time_in': time_in,
                        'time_out': time_out,
                        'recorded_by': request.user
                    }
                )
                created_or_updated.append(obj.id)

            return Response({"message": f"{len(created_or_updated)} ta o'quvchi davomati saqlandi."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceUpdateAPIView(BaseAttendanceAPIView, generics.UpdateAPIView):
    serializer_class = ChildAttendanceSerializer
    
    def get_queryset(self):
        kindergarten = self.get_kindergarten()
        if kindergarten:
            return ChildAttendance.objects.filter(kindergarten=kindergarten)
        return ChildAttendance.objects.none()

class AttendanceDeleteAPIView(BaseAttendanceAPIView, generics.DestroyAPIView):
    serializer_class = ChildAttendanceSerializer
    
    def get_queryset(self):
        kindergarten = self.get_kindergarten()
        if kindergarten:
            return ChildAttendance.objects.filter(kindergarten=kindergarten)
        return ChildAttendance.objects.none()

