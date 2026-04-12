"""
Interface d'administration Django
"""
from django.contrib import admin
from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nationalite', 'nb_livres', 'date_creation']
    search_fields = ['nom', 'nationalite']
    ordering = ['nom']

    def nb_livres(self, obj):
        return obj.livres.count()
    nb_livres.short_description = 'Nombre de livres'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nb_livres']
    search_fields = ['nom']

    def nb_livres(self, obj):
        return obj.livres.count()
    nb_livres.short_description = 'Livres'


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'annee_publication', 'categorie', 'disponible', 'cree_par']
    list_filter = ['categorie', 'disponible', 'annee_publication']
    search_fields = ['titre', 'isbn', 'auteur__nom']
    filter_horizontal = ['tags']
    raw_id_fields = ['auteur', 'cree_par']
    ordering = ['-date_creation']


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'livre', 'date_emprunt', 'date_retour_prevue', 'rendu', 'est_en_retard']
    list_filter = ['rendu']
    search_fields = ['utilisateur__username', 'livre__titre']
    ordering = ['-date_emprunt']

    def est_en_retard(self, obj):
        import datetime
        if obj.rendu:
            return False
        return obj.date_retour_prevue < datetime.date.today()
    est_en_retard.boolean = True
    est_en_retard.short_description = 'En retard ?'


@admin.register(ProfilLecteur)
class ProfilLecteurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'telephone']
    search_fields = ['utilisateur__username', 'utilisateur__email']
    filter_horizontal = ['livres_favoris']
