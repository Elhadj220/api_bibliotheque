# 📚 API Bibliothèque — Django REST Framework

API REST complète de gestion de bibliothèque, développée avec Django REST Framework.

## 🚀 Démarrage rapide

### 1. Cloner et installer

```bash
git clone <url-du-repo>
cd bibliotheque_api

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configurer et lancer

```bash
# Appliquer les migrations
python manage.py migrate

# Peupler avec des données de démonstration
python manage.py seed_data

# Lancer le serveur
python manage.py runserver
```

### 3. Accéder à l'API

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/api/ | Racine de l'API (navigateur DRF) |
| http://127.0.0.1:8000/api/docs/ | Documentation Swagger interactive |
| http://127.0.0.1:8000/api/redoc/ | Documentation ReDoc |
| http://127.0.0.1:8000/admin/ | Interface d'administration Django |

**Comptes de démonstration :**
- `admin` / `Admin1234!` — Superutilisateur
- `lecteur` / `Lecteur1234!` — Lecteur standard

---

## 🔑 Authentification JWT

### Obtenir un token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin1234!"}'
```

Réponse :
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci..."
}
```

### Utiliser le token

```bash
curl http://127.0.0.1:8000/api/livres/ \
  -H "Authorization: Bearer eyJhbGci..."
```

### Rafraîchir le token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJhbGci..."}'
```

---

## 📡 Endpoints

### Authentification

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/register/` | Créer un compte |
| POST | `/api/auth/token/` | Obtenir un token JWT |
| POST | `/api/auth/token/refresh/` | Rafraîchir le token |
| POST | `/api/auth/token/blacklist/` | Déconnecter (invalider token) |
| GET/PUT | `/api/auth/me/` | Mon profil utilisateur |

### Auteurs

| Méthode | URL | Description | Auth |
|---------|-----|-------------|------|
| GET | `/api/auteurs/` | Liste des auteurs | Non |
| POST | `/api/auteurs/` | Créer un auteur | Oui |
| GET | `/api/auteurs/{id}/` | Détail d'un auteur | Non |
| PUT/PATCH | `/api/auteurs/{id}/` | Modifier un auteur | Propriétaire |
| DELETE | `/api/auteurs/{id}/` | Supprimer un auteur | Propriétaire |
| GET | `/api/auteurs/{id}/livres/` | Livres d'un auteur | Non |
| GET | `/api/auteurs/stats/` | Statistiques globales | Non |

### Livres

| Méthode | URL | Description | Auth |
|---------|-----|-------------|------|
| GET | `/api/livres/` | Liste des livres | Non |
| POST | `/api/livres/` | Créer un livre | Oui |
| GET | `/api/livres/{id}/` | Détail d'un livre | Non |
| PUT/PATCH | `/api/livres/{id}/` | Modifier un livre | Propriétaire |
| DELETE | `/api/livres/{id}/` | Supprimer un livre | Propriétaire |
| GET | `/api/livres/disponibles/` | Livres disponibles | Non |
| POST | `/api/livres/{id}/emprunter/` | Emprunter un livre | Oui |
| POST | `/api/livres/{id}/rendre/` | Rendre un livre | Oui |

### Filtres disponibles pour les livres

```
GET /api/livres/?categorie=roman
GET /api/livres/?disponible=true
GET /api/livres/?annee_min=1900&annee_max=2000
GET /api/livres/?auteur_nom=camus
GET /api/livres/?search=miserable        # Recherche titre + auteur + ISBN
GET /api/livres/?ordering=-annee_publication
GET /api/livres/?page=2&size=5
```

### Emprunts, Tags, Profil

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/emprunts/` | Mes emprunts (admin = tous) |
| GET/PUT | `/api/profil/` | Mon profil lecteur |
| GET/POST | `/api/tags/` | Liste/Créer tags |

---

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test api

# Avec détails
python manage.py test api --verbosity=2
```

14 tests couvrent : authentification, CRUD livres/auteurs, validation ISBN, emprunts, filtres.

---

## 🌐 Déploiement

### Render.com (recommandé)

1. Créer un nouveau compte sur [render.com](https://render.com)
2. **New Web Service** → connecter votre repo GitHub
3. Configurer :
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn bibliotheque_project.wsgi`
4. Variables d'environnement :
   ```
   SECRET_KEY=votre-cle-secrete-aleatoire-longue
   DEBUG=False
   ALLOWED_HOSTS=votre-app.onrender.com
   ```
5. Déployer !

### Railway.app

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Déployer
railway login
railway init
railway up
```

Variables à configurer dans le dashboard Railway :
```
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=$RAILWAY_STATIC_URL
```

### VPS (Ubuntu/Debian)

```bash
# Sur le serveur
git clone <repo> /var/www/bibliotheque
cd /var/www/bibliotheque
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Variables d'environnement
export SECRET_KEY="votre-cle"
export DEBUG=False
export ALLOWED_HOSTS="votre-domaine.com"

# Migrations + data
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput

# Lancer avec Gunicorn
gunicorn bibliotheque_project.wsgi --bind 0.0.0.0:8000 --workers 3
```

Pour la production, configurez Nginx comme proxy inverse devant Gunicorn.

---

## 🏗️ Structure du projet

```
bibliotheque_api/
├── manage.py
├── requirements.txt        ← dépendances Python
├── Procfile                ← pour Heroku/Render
├── build.sh                ← script de build
├── .env.example            ← template variables d'env
├── .gitignore
├── bibliotheque_project/
│   ├── settings.py         ← configuration Django
│   ├── urls.py             ← URLs principales
│   └── wsgi.py
└── api/
    ├── models.py           ← Auteur, Tag, Livre, Emprunt, ProfilLecteur
    ├── serializers.py      ← sérialiseurs avec validation
    ├── views.py            ← ViewSets + vues personnalisées
    ├── permissions.py      ← EstProprietaireOuReadOnly
    ├── filters.py          ← LivreFilter, EmpruntFilter
    ├── pagination.py       ← StandardPagination
    ├── urls.py             ← Router + JWT URLs
    ├── admin.py            ← interface d'administration
    ├── tests.py            ← 14 tests automatisés
    └── management/
        └── commands/
            └── seed_data.py ← données de démonstration
```

---

## ⚙️ Configuration (settings.py)

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `DEBUG` | `True` (dev) / `False` (prod) | Mode debug |
| `PAGE_SIZE` | 10 | Éléments par page |
| `ACCESS_TOKEN_LIFETIME` | 60 min | Durée du token d'accès JWT |
| `REFRESH_TOKEN_LIFETIME` | 7 jours | Durée du token de rafraîchissement |
| Throttle anonyme | 100/heure | Limite de requêtes |
| Throttle authentifié | 1000/heure | Limite de requêtes |

---

## 📦 Dépendances

- **Django 4.2** — Framework web
- **djangorestframework** — API REST
- **djangorestframework-simplejwt** — Authentification JWT
- **django-filter** — Filtres avancés
- **drf-spectacular** — Documentation OpenAPI/Swagger
- **whitenoise** — Fichiers statiques en production
- **gunicorn** — Serveur WSGI pour la production
