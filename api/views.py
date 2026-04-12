"""
Vues et ViewSets de l'API Bibliothèque
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import datetime

from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur
from .serializers import (
    AuteurSerializer, AuteurListSerializer,
    TagSerializer,
    LivreSerializer, LivreDetailSerializer,
    EmpruntSerializer,
    ProfilLecteurSerializer,
    UserRegistrationSerializer, UserSerializer
)
from .permissions import EstProprietaireOuReadOnly, EstAdminOuReadOnly
from .filters import LivreFilter, EmpruntFilter
from .pagination import StandardPagination


# ─── AUTEUR ──────────────────────────────────────────────────────────────────

class AuteurViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les auteurs.
    Lecture libre, écriture authentifiée.
    """
    queryset = Auteur.objects.prefetch_related('livres').all()
    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nom', 'nationalite', 'biographie']
    ordering_fields = ['nom', 'nationalite', 'date_creation']
    ordering = ['nom']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuteurListSerializer
        return AuteurSerializer

    @action(detail=True, methods=['get'], url_path='livres')
    def livres(self, request, pk=None):
        """GET /api/auteurs/{id}/livres/ — livres d'un auteur"""
        auteur = self.get_object()
        livres = auteur.livres.select_related('auteur').prefetch_related('tags').all()
        page = self.paginate_queryset(livres)
        if page is not None:
            serializer = LivreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LivreSerializer(livres, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """GET /api/auteurs/stats/ — statistiques globales"""
        from django.db.models import Count, Avg
        data = {
            'total_auteurs': Auteur.objects.count(),
            'total_livres': Livre.objects.count(),
            'total_tags': Tag.objects.count(),
            'total_emprunts': Emprunt.objects.count(),
            'livres_disponibles': Livre.objects.filter(disponible=True).count(),
            'livres_empruntes': Livre.objects.filter(disponible=False).count(),
            'nationalites': list(
                Auteur.objects.values_list('nationalite', flat=True)
                .exclude(nationalite='').distinct()
            ),
            'categories': [
                {'code': c[0], 'label': c[1], 'count': Livre.objects.filter(categorie=c[0]).count()}
                for c in Livre.CATEGORIES
            ],
        }
        return Response(data)


# ─── TAG ─────────────────────────────────────────────────────────────────────

class TagViewSet(viewsets.ModelViewSet):
    """CRUD Tags — admin uniquement pour l'écriture"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [EstAdminOuReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom']
    ordering = ['nom']
    pagination_class = None  # Pas de pagination pour les tags


# ─── LIVRE ───────────────────────────────────────────────────────────────────

class LivreViewSet(viewsets.ModelViewSet):
    """
    CRUD complet pour les livres.
    Actions supplémentaires : disponibles, emprunter, rendre
    """
    queryset = (
        Livre.objects
        .select_related('auteur', 'cree_par')
        .prefetch_related('tags')
        .all()
    )
    permission_classes = [EstProprietaireOuReadOnly]
    pagination_class = StandardPagination
    filterset_class = LivreFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['titre', 'auteur__nom', 'isbn']
    ordering_fields = ['titre', 'annee_publication', 'date_creation', 'categorie']
    ordering = ['-date_creation']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LivreDetailSerializer
        return LivreSerializer

    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)

    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        """GET /api/livres/disponibles/ — livres disponibles à l'emprunt"""
        qs = self.get_queryset().filter(disponible=True)
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LivreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LivreSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='emprunter')
    def emprunter(self, request, pk=None):
        """POST /api/livres/{id}/emprunter/ — emprunter un livre"""
        livre = self.get_object()

        if not livre.disponible:
            return Response(
                {'erreur': f'Le livre "{livre.titre}" n\'est pas disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier que l'utilisateur n'a pas déjà un emprunt actif sur ce livre
        emprunt_existant = Emprunt.objects.filter(
            utilisateur=request.user, livre=livre, rendu=False
        ).first()
        if emprunt_existant:
            return Response(
                {'erreur': 'Vous avez déjà emprunté ce livre.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        date_retour = request.data.get('date_retour_prevue')
        if not date_retour:
            # Par défaut : 14 jours
            date_retour = datetime.date.today() + datetime.timedelta(days=14)

        emprunt = Emprunt.objects.create(
            utilisateur=request.user,
            livre=livre,
            date_retour_prevue=date_retour
        )
        livre.disponible = False
        livre.save()

        serializer = EmpruntSerializer(emprunt)
        return Response(
            {'message': f'"{livre.titre}" emprunté avec succès.', 'emprunt': serializer.data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='rendre')
    def rendre(self, request, pk=None):
        """POST /api/livres/{id}/rendre/ — rendre un livre"""
        livre = self.get_object()
        emprunt = Emprunt.objects.filter(
            utilisateur=request.user, livre=livre, rendu=False
        ).first()

        if not emprunt:
            return Response(
                {'erreur': 'Vous n\'avez pas emprunté ce livre ou il est déjà rendu.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        emprunt.rendu = True
        emprunt.date_retour_effective = datetime.date.today()
        emprunt.save()
        livre.disponible = True
        livre.save()

        return Response({'message': f'"{livre.titre}" rendu avec succès. Merci !'})


# ─── EMPRUNT ─────────────────────────────────────────────────────────────────

class EmpruntViewSet(viewsets.ModelViewSet):
    """
    Emprunts — uniquement les emprunts de l'utilisateur connecté.
    Les admins voient tout.
    """
    serializer_class = EmpruntSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filterset_class = EmpruntFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['date_emprunt', 'date_retour_prevue']
    ordering = ['-date_emprunt']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Emprunt.objects.select_related('utilisateur', 'livre').all()
        return Emprunt.objects.filter(utilisateur=user).select_related('livre')

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


# ─── PROFIL ──────────────────────────────────────────────────────────────────

class ProfilView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/profil/ — profil de l'utilisateur connecté"""
    serializer_class = ProfilLecteurSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profil, _ = ProfilLecteur.objects.get_or_create(utilisateur=self.request.user)
        return profil

    @action(detail=False, methods=['post'], url_path='favoris')
    def ajouter_favori(self, request):
        """POST /api/profil/favoris/ — ajouter un livre aux favoris"""
        profil, _ = ProfilLecteur.objects.get_or_create(utilisateur=request.user)
        livre_id = request.data.get('livre_id')
        livre = get_object_or_404(Livre, pk=livre_id)
        profil.livres_favoris.add(livre)
        return Response({'message': f'"{livre.titre}" ajouté aux favoris.'})


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — inscription d'un nouvel utilisateur"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': f'Compte créé avec succès pour {user.username}.', 'username': user.username},
            status=status.HTTP_201_CREATED
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/auth/me/ — informations de l'utilisateur connecté"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
