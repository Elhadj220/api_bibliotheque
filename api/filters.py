"""
Filtres avancés
"""
import django_filters
from .models import Livre, Emprunt


class LivreFilter(django_filters.FilterSet):
    categorie = django_filters.ChoiceFilter(choices=Livre.CATEGORIES)
    annee_min = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='gte')
    annee_max = django_filters.NumberFilter(field_name='annee_publication', lookup_expr='lte')
    titre = django_filters.CharFilter(lookup_expr='icontains')
    auteur_nom = django_filters.CharFilter(field_name='auteur__nom', lookup_expr='icontains')
    disponible = django_filters.BooleanFilter()
    tag = django_filters.CharFilter(field_name='tags__nom', lookup_expr='icontains')

    class Meta:
        model = Livre
        fields = ['categorie', 'disponible']


class EmpruntFilter(django_filters.FilterSet):
    rendu = django_filters.BooleanFilter()
    date_min = django_filters.DateFilter(field_name='date_emprunt', lookup_expr='gte')
    date_max = django_filters.DateFilter(field_name='date_emprunt', lookup_expr='lte')

    class Meta:
        model = Emprunt
        fields = ['rendu']
