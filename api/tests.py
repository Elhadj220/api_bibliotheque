"""
Tests automatisés pour l'API Bibliothèque
Usage : python manage.py test api
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Auteur, Tag, Livre, Emprunt, ProfilLecteur
import datetime


class AuteurTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'Admin1234!')
        self.user = User.objects.create_user('user', 'user@test.com', 'User1234!')
        self.auteur = Auteur.objects.create(nom='Victor Hugo', nationalite='Française')

    def test_list_auteurs_anonymous(self):
        """Lecture libre pour les anonymes"""
        response = self.client.get('/api/auteurs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_auteur_authenticated(self):
        """Création nécessite une authentification"""
        self.client.force_authenticate(user=self.user)
        data = {'nom': 'Albert Camus', 'nationalite': 'Française'}
        response = self.client.post('/api/auteurs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_auteur_anonymous_fails(self):
        """Création refusée sans authentification"""
        data = {'nom': 'Molière', 'nationalite': 'Française'}
        response = self.client.post('/api/auteurs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_endpoint(self):
        """Endpoint stats accessible"""
        response = self.client.get('/api/auteurs/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_auteurs', response.data)


class LivreTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'Admin1234!')
        self.user = User.objects.create_user('user', 'user@test.com', 'User1234!')
        self.auteur = Auteur.objects.create(nom='Albert Camus', nationalite='Française', biographie='Écrivain.')
        self.livre = Livre.objects.create(
            titre="L'Étranger", isbn='9782070360024',
            annee_publication=1942, categorie='roman',
            auteur=self.auteur, cree_par=self.admin
        )

    def test_list_livres(self):
        response = self.client.get('/api/livres/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_livre_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'titre': 'La Peste', 'isbn': '9782070360178',
            'annee_publication': 1947, 'categorie': 'roman',
            'auteur_id': self.auteur.id
        }
        response = self.client.post('/api/livres/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_isbn_validation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'titre': 'Mauvais ISBN', 'isbn': 'INVALID',
            'annee_publication': 2000, 'categorie': 'roman',
            'auteur_id': self.auteur.id
        }
        response = self.client.post('/api/livres/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_emprunter_livre(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/livres/{self.livre.id}/emprunter/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.livre.refresh_from_db()
        self.assertFalse(self.livre.disponible)

    def test_emprunter_livre_indisponible(self):
        self.livre.disponible = False
        self.livre.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/livres/{self.livre.id}/emprunter/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtres_categorie(self):
        response = self.client.get('/api/livres/?categorie=roman')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search(self):
        response = self.client.get('/api/livres/?search=Camus')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthTests(APITestCase):

    def test_register(self):
        data = {
            'username': 'nouveau', 'email': 'nouveau@test.com',
            'password': 'Nouveau1234!', 'password_confirm': 'Nouveau1234!'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_obtain_token(self):
        User.objects.create_user('testuser', password='Test1234!')
        data = {'username': 'testuser', 'password': 'Test1234!'}
        response = self.client.post('/api/auth/token/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_me_authenticated(self):
        user = User.objects.create_user('meuser', password='Me1234!')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
