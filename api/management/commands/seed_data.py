from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Auteur, Tag, Livre, Emprunt, ProfilLecteur
import datetime

class Command(BaseCommand):
    help = 'Peuple la base de donnees avec des donnees de demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creation des donnees de test...')

        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@bibliotheque.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('Admin1234!')
            admin.save()
            self.stdout.write('Admin cree (admin / Admin1234!)')

        lecteur, created = User.objects.get_or_create(
            username='lecteur',
            defaults={'email': 'lecteur@bibliotheque.com', 'first_name': 'Marie', 'last_name': 'Diop'}
        )
        if created:
            lecteur.set_password('Lecteur1234!')
            lecteur.save()
            ProfilLecteur.objects.get_or_create(utilisateur=lecteur)
            self.stdout.write('Lecteur cree (lecteur / Lecteur1234!)')

        tags_data = ['Classique', 'Contemporain', 'Philosophie', 'Prix Nobel', 'Bestseller',
                     'Science-Fiction', 'Autobiographie', 'Poetique', 'Politique', 'Afrique']
        tags = {}
        for t in tags_data:
            tag, _ = Tag.objects.get_or_create(nom=t)
            tags[t] = tag

        auteurs_data = [
            {'nom': 'Albert Camus', 'nationalite': 'Francaise', 'biographie': 'Ecrivain, philosophe et journaliste francais. Prix Nobel de Litterature en 1957.'},
            {'nom': 'Mariama Ba', 'nationalite': 'Senegalaise', 'biographie': 'Romanciere senegalaise, auteure de Une si longue lettre, chef-oeuvre de la litterature africaine.'},
            {'nom': 'Cheikh Hamidou Kane', 'nationalite': 'Senegalaise', 'biographie': 'Ecrivain senegalais, auteur de Aventure ambigue, roman phare de la litterature africaine.'},
            {'nom': 'Victor Hugo', 'nationalite': 'Francaise', 'biographie': 'Poete, romancier et dramaturge francais du XIXe siecle. Auteur de Les Miserables.'},
            {'nom': 'Chinua Achebe', 'nationalite': 'Nigeriane', 'biographie': 'Romancier nigerian, pere de la litterature africaine moderne.'},
            {'nom': 'Simone de Beauvoir', 'nationalite': 'Francaise', 'biographie': 'Philosophe, romanciere et essayiste francaise. Figure du feminisme existentialiste.'},
            {'nom': 'Leopold Sedar Senghor', 'nationalite': 'Senegalaise', 'biographie': 'Poete et premier president du Senegal. Pere de la Negritude.'},
        ]
        auteurs = {}
        for a in auteurs_data:
            auteur, _ = Auteur.objects.get_or_create(nom=a['nom'], defaults=a)
            auteurs[a['nom']] = auteur

        livres_data = [
            {'titre': "L'Etranger", 'isbn': '9782070360024', 'annee_publication': 1942, 'categorie': 'roman', 'auteur': auteurs['Albert Camus'], 'disponible': True, 'tags': ['Classique', 'Philosophie', 'Prix Nobel']},
            {'titre': 'La Peste', 'isbn': '9782070360178', 'annee_publication': 1947, 'categorie': 'roman', 'auteur': auteurs['Albert Camus'], 'disponible': True, 'tags': ['Classique', 'Prix Nobel']},
            {'titre': 'Une si longue lettre', 'isbn': '9782708704176', 'annee_publication': 1979, 'categorie': 'roman', 'auteur': auteurs['Mariama Ba'], 'disponible': True, 'tags': ['Classique', 'Afrique']},
            {'titre': "L'Aventure ambigue", 'isbn': '9782264007858', 'annee_publication': 1961, 'categorie': 'roman', 'auteur': auteurs['Cheikh Hamidou Kane'], 'disponible': True, 'tags': ['Classique', 'Afrique', 'Philosophie']},
            {'titre': 'Les Miserables', 'isbn': '9782070409228', 'annee_publication': 1862, 'categorie': 'roman', 'auteur': auteurs['Victor Hugo'], 'disponible': True, 'tags': ['Classique', 'Politique']},
            {'titre': 'Things Fall Apart', 'isbn': '9780385474542', 'annee_publication': 1958, 'categorie': 'roman', 'auteur': auteurs['Chinua Achebe'], 'disponible': True, 'tags': ['Classique', 'Afrique']},
            {'titre': 'Le Deuxieme Sexe', 'isbn': '9782070205134', 'annee_publication': 1949, 'categorie': 'essai', 'auteur': auteurs['Simone de Beauvoir'], 'disponible': True, 'tags': ['Philosophie', 'Classique', 'Politique']},
            {'titre': "Chants d'Ombre", 'isbn': '9782020060882', 'annee_publication': 1945, 'categorie': 'poesie', 'auteur': auteurs['Leopold Sedar Senghor'], 'disponible': True, 'tags': ['Afrique', 'Poetique']},
            {'titre': 'Notre-Dame de Paris', 'isbn': '9782070409617', 'annee_publication': 1831, 'categorie': 'roman', 'auteur': auteurs['Victor Hugo'], 'disponible': False, 'tags': ['Classique']},
            {'titre': 'Le Mythe de Sisyphe', 'isbn': '9782070322886', 'annee_publication': 1942, 'categorie': 'essai', 'auteur': auteurs['Albert Camus'], 'disponible': True, 'tags': ['Philosophie', 'Prix Nobel']},
        ]

        for l in livres_data:
            tags_list = l.pop('tags')
            livre, created = Livre.objects.get_or_create(isbn=l['isbn'], defaults={**l, 'cree_par': admin})
            if created:
                for tag_nom in tags_list:
                    if tag_nom in tags:
                        livre.tags.add(tags[tag_nom])

        livre_emprunte = Livre.objects.filter(disponible=False).first()
        if livre_emprunte:
            Emprunt.objects.get_or_create(
                utilisateur=lecteur, livre=livre_emprunte, rendu=False,
                defaults={'date_retour_prevue': datetime.date.today() + datetime.timedelta(days=7)}
            )

        self.stdout.write(self.style.SUCCESS('Base de donnees peuplee avec succes!'))
        self.stdout.write('Comptes: admin/Admin1234! et lecteur/Lecteur1234!')
        self.stdout.write('Documentation: http://127.0.0.1:8000/api/docs/')
