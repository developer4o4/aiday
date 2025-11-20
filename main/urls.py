# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='api_token_auth'),
    
    # Public endpoints (hammaga ochiq)
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('qrcode/<str:qr_code>/', views.user_by_qrcode, name='user-by-qrcode'),
    
    # Admin endpoints (faqat adminlar uchun)
    path('super/users/', views.UserListCreateView.as_view(), name='admin-user-list'),
    path('super/users/<int:pk>/', views.UserDetailView.as_view(), name='admin-user-detail'),
    path('super/all-users/', views.AdminUserListView.as_view(), name='admin-all-users'),
    path('super/qrcodes/', views.QrcodeListView.as_view(), name='admin-qrcode-list'),
    
    # Debug endpoint (agar qo'shgan bo'lsangiz)
    # path('debug-auth/', views.debug_auth, name='debug-auth'),
]