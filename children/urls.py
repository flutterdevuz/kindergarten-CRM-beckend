from django.urls import path
from .views import ChildListAPIView, ChildCreateAPIView, ChildRetrieveAPIView, ChildUpdateAPIView, ChildDeleteAPIView

app_name = 'children'

urlpatterns = [
    path('kindergarden/children/', ChildListAPIView.as_view(), name='child_list'),
    path('kindergarden/children/add/', ChildCreateAPIView.as_view(), name='child_add'),
    path('kindergarden/children/<str:pk>/', ChildRetrieveAPIView.as_view(), name='child_detail'),
    path('kindergarden/children/<str:pk>/edit/', ChildUpdateAPIView.as_view(), name='child_edit'),
    path('kindergarden/children/<str:pk>/delete/', ChildDeleteAPIView.as_view(), name='child_delete'),
]
