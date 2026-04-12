"""
Permissions personnalisées
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class EstProprietaireOuReadOnly(BasePermission):
    """
    Lecture libre pour tous.
    Écriture uniquement pour le créateur ou un admin.
    """
    message = 'Vous devez être le propriétaire pour modifier cet objet.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        # Vérifie le champ cree_par si présent
        if hasattr(obj, 'cree_par'):
            return obj.cree_par == request.user
        # Pour les emprunts
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user
        return False


class EstAdminOuReadOnly(BasePermission):
    """Lecture pour tous, écriture uniquement pour les admins."""
    message = 'Seuls les administrateurs peuvent effectuer cette action.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
