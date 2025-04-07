# 🎯 Application de Gestion des Tickets

Bienvenue dans **TicketManager**, une application web développée avec **Django** permettant la gestion de projets et de tickets. Elle offre une interface intuitive pour les administrateurs et les membres d'équipe, favorisant un suivi clair et collaboratif.

## 🚀 Fonctionnalités

- Authentification des utilisateurs (connexion, inscription, réinitialisation du mot de passe)
- Gestion des projets (ajout, assignation aux membres)
- Création, mise à jour et suivi des tickets (avec éditeur de texte enrichi)
- Filtres et tri (par statut, date, ordre alphabétique)
- Interface admin complète (gestion des membres, projets, statistiques)
- Interface membre personnalisée (tickets assignés, historique, remarques)
- Tableau de bord avec statistiques clés
- Upload de fichiers (ex: CV, justificatifs)
- Pagination, commentaires, et notifications internes

## 🛠️ Stack Technique

- **Backend** : Django (Python)
- **Frontend** : HTML, CSS (Bootstrap), JavaScript
- **Base de données** : SQLite (ou autre selon config)
- **Autres outils** : Django Admin, RichText, Django Filters, Bootstrap Icons...

## 📦 Installation

1. **Cloner le dépôt :**
   ```bash
   git clone [https://github.com/ton-pseudo/ticketmanager.git](https://github.com/IlyasBBB/Gestion-de-projets.git)
   cd Gestion-de-projets

2. **Créer un environnement virtuel :**

   ```bash

   python -m venv env
   source env/bin/activate   # sous Windows : env\Scripts\activate

3. **Appliquer les migrations :**

   ```bash
   python manage.py migrate

4. **Créer un superutilisateur (admin) :**

   ```bash
   python manage.py createsuperuser

5. **Lancer le serveur de développement :**

   ```bash
   python manage.py runserver
   Accéder à l'app via : http://127.0.0.1:8000

##✅ À faire / Améliorations possibles
Intégration d’un système de notifications en temps réel (via Django Channels)

Authentification OAuth2

API REST (Django REST Framework)

Responsive design amélioré

Gestion des rôles plus fine
