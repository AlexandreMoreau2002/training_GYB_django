# Summit API - Backend Django

Guide complet pour comprendre et utiliser l'API du blog escalade Summit.

## Table des matières

1. [C'est quoi tout ça ?](#cest-quoi-tout-ça-)
2. [Comment lancer le projet](#comment-lancer-le-projet)
3. [Structure du projet](#structure-du-projet)
4. [Les concepts clés expliqués](#les-concepts-clés-expliqués)
5. [Tester l'API](#tester-lapi)
6. [Commandes utiles](#commandes-utiles)

---

## C'est quoi tout ça ?

### Django
**Django** est un framework Python pour créer des sites web et des APIs. Il gère automatiquement plein de choses : la base de données, les URLs, l'authentification, etc.

### Django REST Framework (DRF)
**DRF** est une extension de Django spécialisée pour créer des **APIs REST**. Une API REST, c'est un serveur qui répond à des requêtes HTTP (GET, POST, PUT, DELETE) et renvoie des données en JSON.

Exemple : quand tu vas sur `/api/articles/`, le serveur te renvoie la liste des articles en JSON.

### La base de données : SQLite
On utilise **SQLite** - c'est une base de données stockée dans un simple fichier (`db.sqlite3`). Pas besoin d'installer un serveur de base de données comme PostgreSQL ou MySQL. C'est parfait pour le développement.

Le fichier `db.sqlite3` contient toutes les données : utilisateurs, articles, commentaires, etc.

### JWT (JSON Web Token)
C'est le système d'authentification qu'on utilise. Quand tu te connectes :
1. Tu envoies ton username/password
2. Le serveur te renvoie un **token** (une longue chaîne de caractères)
3. Pour les requêtes suivantes, tu envoies ce token pour prouver que tu es connecté

Le token expire après un certain temps (1 heure par défaut).

---

## Comment lancer le projet

### 1. Activer l'environnement virtuel

Un **environnement virtuel** isole les dépendances Python de ce projet. Ça évite les conflits avec d'autres projets.

```bash
cd backend
source .venv/bin/activate
```

Tu verras `(.venv)` apparaître au début de ta ligne de commande. Ça veut dire que l'environnement est activé.

### 2. Vérifier que les migrations sont appliquées

Les **migrations** sont des fichiers qui décrivent la structure de la base de données. Elles permettent de créer/modifier les tables.

```bash
python manage.py migrate
```

Si tu vois "No migrations to apply", c'est que tout est déjà en place.

### 3. Peupler la base de données (optionnel)

La commande `seed` crée des données de test :

```bash
python manage.py seed
```

Ça crée :
- 1 admin (login: `admin`, password: `admin123`)
- 5 utilisateurs de test
- 4 catégories (Bloc, Voie, Grande Voie, Alpinisme)
- 15 tags
- 15 articles
- ~70 commentaires

Pour tout effacer et recréer :
```bash
python manage.py seed --clear
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

Le serveur tourne sur `http://127.0.0.1:8000`

Pour arrêter : `Ctrl+C`

---

## Structure du projet

```
backend/
├── .venv/              # Environnement virtuel Python (les dépendances)
├── apps/               # Nos applications Django
│   ├── articles/       # Tout ce qui concerne les articles
│   │   ├── models.py       # Les modèles (structure des données)
│   │   ├── serializers.py  # Conversion Python ↔ JSON
│   │   ├── views.py        # La logique des endpoints
│   │   ├── urls.py         # Les routes de l'API
│   │   └── admin.py        # Interface d'admin Django
│   └── users/          # Tout ce qui concerne les utilisateurs
│       ├── models.py       # Le modèle Profile
│       ├── serializers.py  # Serializers utilisateur
│       ├── views.py        # Endpoint /me
│       ├── urls.py         # Routes utilisateur
│       └── signals.py      # Création auto du profil
├── src/                # Configuration du projet Django
│   ├── settings.py     # Toute la configuration
│   └── urls.py         # Routes principales
├── db.sqlite3          # La base de données
├── manage.py           # Commande Django
└── api.http            # Fichier pour tester l'API
```

---

## Les concepts clés expliqués

### Models (Modèles)

Un **modèle** définit la structure d'une table en base de données. C'est une classe Python.

```python
class Article(models.Model):
    title = models.CharField(max_length=200)      # Texte court
    content = models.TextField()                   # Texte long
    author = models.ForeignKey(User)              # Relation vers User
    tags = models.ManyToManyField(Tag)            # Relation multiple
```

Nos modèles :
- **User** : Utilisateur Django (fourni par Django)
- **Profile** : Extension du User (bio, avatar, website)
- **Category** : Catégorie d'article (Bloc, Voie, etc.)
- **Tag** : Étiquette pour les articles
- **Article** : Un article de blog
- **Comment** : Commentaire sur un article (peut avoir des réponses)

### Relations entre modèles

- **ForeignKey** (FK) : Une relation "appartient à" (un article a UN auteur)
- **ManyToMany** (M2M) : Une relation "plusieurs à plusieurs" (un article a PLUSIEURS tags, un tag est sur PLUSIEURS articles)
- **OneToOne** : Une relation "un pour un" (un User a UN Profile)

### Serializers

Un **serializer** convertit les objets Python en JSON (et vice versa).

```python
# L'objet Python
article = Article(title="Mon titre", content="...")

# Le serializer le transforme en JSON
{
    "id": 1,
    "title": "Mon titre",
    "content": "...",
    "author": {"id": 1, "username": "admin"}
}
```

On a différents serializers pour différents usages :
- `ArticleListSerializer` : Version légère pour les listes
- `ArticleDetailSerializer` : Version complète avec commentaires
- `ArticleCreateUpdateSerializer` : Pour créer/modifier

### ViewSets

Un **ViewSet** gère toutes les actions sur un modèle :
- `list` : GET /articles/ → Liste
- `retrieve` : GET /articles/mon-slug/ → Détail
- `create` : POST /articles/ → Créer
- `update` : PUT /articles/mon-slug/ → Modifier tout
- `partial_update` : PATCH /articles/mon-slug/ → Modifier partiellement
- `destroy` : DELETE /articles/mon-slug/ → Supprimer

### URLs et Routers

Le **Router** génère automatiquement les URLs pour un ViewSet :

```python
router.register('articles', ArticleViewSet)
# Génère automatiquement :
# GET/POST     /api/articles/
# GET/PUT/DELETE /api/articles/<slug>/
```

### Signals

Un **signal** est un événement qui déclenche une action. On l'utilise pour créer automatiquement un Profile quand un User est créé :

```python
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

### Slug

Un **slug** est une version "URL-friendly" d'un texte :
- "Mon Super Article !" → `mon-super-article`

On l'utilise dans les URLs au lieu de l'ID pour que ce soit plus lisible :
- `/api/articles/42/` → `/api/articles/mon-super-article/`

### Pagination

Quand tu as beaucoup de données, l'API ne renvoie pas tout d'un coup. Elle renvoie **page par page** (10 éléments par défaut) :

```json
{
    "count": 50,
    "next": "http://localhost:8000/api/articles/?page=2",
    "previous": null,
    "results": [...]
}
```

### Filtres

Tu peux filtrer les résultats avec des paramètres URL :
- `/api/articles/?category__slug=bloc` → Articles de la catégorie Bloc
- `/api/articles/?search=escalade` → Recherche "escalade"
- `/api/articles/?ordering=-published_at` → Triés par date (récents d'abord)

---

## Tester l'API

### Option 1 : Fichier api.http (recommandé)

1. Installe l'extension **REST Client** dans VS Code
2. Ouvre le fichier `api.http`
3. Clique sur "Send Request" au-dessus de chaque requête

### Option 2 : Interface web de DRF

1. Lance le serveur : `python manage.py runserver`
2. Va sur `http://127.0.0.1:8000/api/`
3. Tu as une interface web pour naviguer dans l'API

### Option 3 : curl en terminal

```bash
# Liste des articles
curl http://127.0.0.1:8000/api/articles/

# Login (récupère le token)
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Requête authentifiée (remplace TOKEN par le vrai token)
curl http://127.0.0.1:8000/api/me/ \
  -H "Authorization: Bearer TOKEN"
```

### Option 4 : Admin Django

1. Va sur `http://127.0.0.1:8000/admin/`
2. Connecte-toi avec `admin` / `admin123`
3. Tu peux voir et modifier toutes les données

---

## Commandes utiles

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer le serveur
python manage.py runserver

# Appliquer les migrations
python manage.py migrate

# Créer de nouvelles migrations (après modif des models)
python manage.py makemigrations

# Peupler la base de données
python manage.py seed
python manage.py seed --clear  # Efface et recrée tout

# Créer un superuser manuellement
python manage.py createsuperuser

# Ouvrir un shell Python avec Django chargé
python manage.py shell

# Vérifier que tout est OK
python manage.py check
```

---

## Endpoints de l'API

| Méthode | URL | Description | Auth requise |
|---------|-----|-------------|--------------|
| POST | `/api/auth/login/` | Se connecter (obtenir token) | Non |
| POST | `/api/auth/refresh/` | Rafraîchir le token | Non |
| GET | `/api/me/` | Mon profil | Oui |
| PATCH | `/api/me/` | Modifier mon profil | Oui |
| GET | `/api/articles/` | Liste des articles | Non |
| POST | `/api/articles/` | Créer un article | Oui |
| GET | `/api/articles/<slug>/` | Détail d'un article | Non |
| PUT/PATCH | `/api/articles/<slug>/` | Modifier un article | Oui (auteur) |
| DELETE | `/api/articles/<slug>/` | Supprimer un article | Oui (auteur) |
| GET | `/api/articles/<slug>/comments/` | Commentaires d'un article | Non |
| POST | `/api/articles/<slug>/comments/` | Ajouter un commentaire | Oui |
| GET | `/api/categories/` | Liste des catégories | Non |
| GET | `/api/categories/<slug>/` | Détail d'une catégorie | Non |
| GET | `/api/tags/` | Liste des tags | Non |

---

## Résumé de ce qui a été fait

1. **Installation des dépendances** : djangorestframework, JWT, CORS, django-filter, Faker
2. **Création des modèles** : Profile, Category, Tag, Article, Comment
3. **Migrations** : Création des tables en base de données
4. **Serializers** : Conversion des données Python ↔ JSON
5. **ViewSets** : Logique des endpoints (CRUD)
6. **URLs** : Routage de l'API
7. **Authentification JWT** : Login/Logout avec tokens
8. **Commande seed** : Génération de données de test
9. **Configuration CORS** : Pour que le frontend puisse appeler l'API

L'API est prête à être consommée par le frontend Next.js !
