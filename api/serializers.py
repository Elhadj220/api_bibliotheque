"""
Sérialiseurs de l'API Bibliothèque
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur
import datetime


# ─── AUTEUR ──────────────────────────────────────────────────────────────────

class AuteurSerializer(serializers.ModelSerializer):
    nombre_livres = serializers.SerializerMethodField()

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'biographie', 'nationalite', 'nombre_livres', 'date_creation']
        read_only_fields = ['id', 'date_creation', 'nombre_livres']

    def get_nombre_livres(self, obj):
        return obj.livres.count()


class AuteurListSerializer(serializers.ModelSerializer):
    """Sérialiseur allégé pour les listes"""
    nombre_livres = serializers.SerializerMethodField()

    class Meta:
        model = Auteur
        fields = ['id', 'nom', 'nationalite', 'nombre_livres']

    def get_nombre_livres(self, obj):
        return obj.livres.count()


# ─── TAG ─────────────────────────────────────────────────────────────────────

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom']


# ─── LIVRE ───────────────────────────────────────────────────────────────────

class LivreSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    auteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(),
        source='auteur',
        write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    cree_par_username = serializers.SerializerMethodField()

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'auteur_id', 'auteur_nom', 'tags', 'tag_ids',
            'disponible', 'cree_par_username', 'date_creation'
        ]
        read_only_fields = ['id', 'date_creation', 'auteur_nom', 'cree_par_username']

    def get_auteur_nom(self, obj):
        return obj.auteur.nom if obj.auteur else None

    def get_cree_par_username(self, obj):
        return obj.cree_par.username if obj.cree_par else None

    def validate_isbn(self, value):
        clean = value.replace('-', '').replace(' ', '')
        if not clean.isdigit() or len(clean) != 13:
            raise serializers.ValidationError("L'ISBN doit contenir exactement 13 chiffres.")
        return value

    def validate_annee_publication(self, value):
        if value < 1000 or value > 2025:
            raise serializers.ValidationError("L'année doit être entre 1000 et 2025.")
        return value

    def validate(self, data):
        if data.get('categorie') == 'essai':
            auteur = data.get('auteur')
            if auteur and not auteur.biographie:
                raise serializers.ValidationError(
                    "Les essais nécessitent une biographie de l'auteur."
                )
        return data


class LivreDetailSerializer(LivreSerializer):
    """Sérialiseur détaillé avec auteur imbriqué"""
    auteur = AuteurListSerializer(read_only=True)

    class Meta(LivreSerializer.Meta):
        fields = [
            'id', 'titre', 'isbn', 'annee_publication', 'categorie',
            'auteur', 'auteur_id', 'tags', 'tag_ids',
            'disponible', 'cree_par_username', 'date_creation'
        ]


# ─── EMPRUNT ─────────────────────────────────────────────────────────────────

class EmpruntSerializer(serializers.ModelSerializer):
    utilisateur_username = serializers.SerializerMethodField()
    livre_titre = serializers.SerializerMethodField()
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur', 'utilisateur_username',
            'livre', 'livre_titre',
            'date_emprunt', 'date_retour_prevue',
            'rendu', 'date_retour_effective', 'est_en_retard'
        ]
        read_only_fields = ['id', 'date_emprunt', 'utilisateur', 'est_en_retard']

    def get_utilisateur_username(self, obj):
        return obj.utilisateur.username

    def get_livre_titre(self, obj):
        return obj.livre.titre

    def get_est_en_retard(self, obj):
        if obj.rendu:
            return False
        return obj.date_retour_prevue < datetime.date.today()

    def validate_date_retour_prevue(self, value):
        if value <= datetime.date.today():
            raise serializers.ValidationError("La date de retour doit être dans le futur.")
        return value


# ─── PROFIL ──────────────────────────────────────────────────────────────────

class ProfilLecteurSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    livres_favoris = LivreSerializer(many=True, read_only=True)
    livres_favoris_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Livre.objects.all(),
        source='livres_favoris',
        write_only=True,
        required=False
    )

    class Meta:
        model = ProfilLecteur
        fields = [
            'id', 'username', 'email',
            'adresse', 'telephone', 'date_naissance', 'bio',
            'livres_favoris', 'livres_favoris_ids'
        ]
        read_only_fields = ['id', 'username', 'email']

    def get_username(self, obj):
        return obj.utilisateur.username

    def get_email(self, obj):
        return obj.utilisateur.email


# ─── UTILISATEUR / AUTH ───────────────────────────────────────────────────────

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Les mots de passe ne correspondent pas.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        ProfilLecteur.objects.create(utilisateur=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'is_staff', 'date_joined']
