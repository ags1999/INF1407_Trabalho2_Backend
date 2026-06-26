from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core import views

# Router para o CRUD de livros (gera automaticamente as rotas REST)
router = DefaultRouter()
router.register(r'livros', views.LivroViewSet, basename='livro')

urlpatterns = [
    # Autenticação (JWT)
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/activate/', views.ActivateAccountView.as_view(), name='activate'),

    # Gerência de senha
    path('auth/password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    path('auth/password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Perfil do usuário
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Busca no Google Books
    path('search/', views.BookSearchView.as_view(), name='search'),

    # CRUD de livros
    path('', include(router.urls)),
]
