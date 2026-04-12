"""
Modèles de l'API Bibliothèque
- Auteur, Tag, Livre, Emprunt, ProfilLecteur
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Auteur(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom complet')
    biographie = models.TextField(blank=True, null=True, verbose_name='Biographie')
    nationalite = models.CharField(max_length=100, blank=True, default='', verbose_name='Nationalité')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name='Tag')

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Livre(models.Model):
    CATEGORIES = [
        ('roman', 'Roman'),
        ('essai', 'Essai'),
        ('poesie', 'Poésie'),
        ('bd', 'Bande dessinée'),
        ('science', 'Science'),
        ('histoire', 'Histoire'),
        ('biographie', 'Biographie'),
        ('jeunesse', 'Jeunesse'),
        ('autre', 'Autre'),
    ]

    titre = models.CharField(max_length=300, verbose_name='Titre')
    isbn = models.CharField(max_length=17, unique=True, verbose_name='ISBN')
    annee_publication = models.IntegerField(
        verbose_name='Année de publication',
        validators=[MinValueValidator(1000), MaxValueValidator(2025)]
    )
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='roman', verbose_name='Catégorie')
    auteur = models.ForeignKey(
        Auteur,
        on_delete=models.CASCADE,
        related_name='livres',
        verbose_name='Auteur'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='livres', verbose_name='Tags')
    disponible = models.BooleanField(default=True, verbose_name='Disponible')
    cree_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livres_crees',
        verbose_name='Créé par'
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    def __str__(self):
        return f'{self.titre} ({self.annee_publication})'

    class Meta:
        ordering = ['-annee_publication', 'titre']
        verbose_name = 'Livre'
        verbose_name_plural = 'Livres'


class Emprunt(models.Model):
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emprunts',
        verbose_name='Utilisateur'
    )
    livre = models.ForeignKey(
        Livre,
        on_delete=models.CASCADE,
        related_name='emprunts',
        verbose_name='Livre'
    )
    date_emprunt = models.DateField(auto_now_add=True, verbose_name='Date d\'emprunt')
    date_retour_prevue = models.DateField(verbose_name='Date de retour prévue')
    rendu = models.BooleanField(default=False, verbose_name='Rendu')
    date_retour_effective = models.DateField(null=True, blank=True, verbose_name='Date de retour effective')

    def __str__(self):
        return f'{self.utilisateur.username} — {self.livre.titre}'

    class Meta:
        ordering = ['-date_emprunt']
        verbose_name = 'Emprunt'
        verbose_name_plural = 'Emprunts'


class ProfilLecteur(models.Model):
    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name='Utilisateur'
    )
    adresse = models.TextField(blank=True, default='', verbose_name='Adresse')
    telephone = models.CharField(max_length=20, blank=True, default='', verbose_name='Téléphone')
    date_naissance = models.DateField(null=True, blank=True, verbose_name='Date de naissance')
    livres_favoris = models.ManyToManyField(
        Livre,
        blank=True,
        related_name='lecteurs_favoris',
        verbose_name='Livres favoris'
    )
    bio = models.TextField(blank=True, default='', verbose_name='Biographie lecteur')

    def __str__(self):
        return f'Profil de {self.utilisateur.username}'

    class Meta:
        verbose_name = 'Profil Lecteur'
        verbose_name_plural = 'Profils Lecteurs'
