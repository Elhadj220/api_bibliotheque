"""
URLs de l'API Bibliothèque
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import (
    AuteurViewSet, TagViewSet, LivreViewSet,
    EmpruntViewSet, ProfilView, RegisterView, MeView
)

router = DefaultRouter()
router.register(r'auteurs', AuteurViewSet, basename='auteur')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'livres', LivreViewSet, basename='livre')
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')

urlpatterns = [
    # API REST
    path('', include(router.urls)),
    # Authentification JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', MeView.as_view(), name='me'),
    # Profil
    path('profil/', ProfilView.as_view(), name='profil'),
]
