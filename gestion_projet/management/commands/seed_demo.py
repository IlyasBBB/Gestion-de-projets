"""Charge des données de démonstration fictives (comptes, projets, tickets)."""

from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from gestion_projet.models import Admin, Comment, Membre, Notification, Projet, Ticket

MOT_DE_PASSE_DEMO = "projex-demo"

MEMBRES = [
    ("salma", "Amrani", "Salma"),
    ("youssef", "Idrissi", "Youssef"),
    ("hind", "Tazi", "Hind"),
]

PROJETS = [
    ("Pilotage des stocks", "Suivi des niveaux de stock et des alertes de réapprovisionnement.",
     ["salma", "youssef"]),
    ("Portail achats", "Circuit de demande et de validation des achats.", ["youssef", "hind"]),
    ("Maintenance", "Déclaration et historique des interventions sur les équipements.", ["hind", "salma"]),
]

# (projet, auteur, type, intitulé, état visé, remarque de rejet)
TICKETS = [
    (0, "salma", "anomalie", "Écart de stock après inventaire", "declare", None),
    (1, "youssef", "parametrage", "Ajout d'un circuit de validation pour les achats urgents", "declare", None),
    (2, "hind", "info", "Accès à l'historique des interventions de 2023", "declare", None),
    (1, "hind", "parametrage", "Nouveau profil approbateur pour le service achats", "analyse", None),
    (0, "youssef", "anomalie", "Les seuils d'alerte ne se déclenchent plus", "analyse", None),
    (2, "salma", "info", "Export mensuel des arrêts machine", "traitement", None),
    (1, "youssef", "anomalie", "Pièce jointe refusée au dépôt d'une demande", "traitement", None),
    (1, "hind", "anomalie", "Doublons dans la liste des fournisseurs", "cloture", None),
    (0, "salma", "parametrage", "Unité de mesure manquante sur trois articles", "cloture", None),
    (2, "hind", "parametrage", "Droits de lecture pour l'équipe qualité", "rejete",
     "Déjà couvert par le ticket « Accès à l'historique des interventions ». Merci de le suivre."),
]

CHEMIN = {
    "declare": [],
    "analyse": ["analyse"],
    "traitement": ["analyse", "traitement"],
    "cloture": ["analyse", "traitement", "cloture"],
    "rejete": ["analyse", "rejete"],
}


class Command(BaseCommand):
    help = "Remplace les données par un jeu de démonstration fictif."

    @transaction.atomic
    def handle(self, *args, **options):
        Ticket.objects.all().delete()
        Projet.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        admin_user = User.objects.create_user("admin", password=MOT_DE_PASSE_DEMO)
        Admin.objects.create(user=admin_user, nom="Démo", prenom="Admin",
                             telephone="-", email="admin@projex.demo")

        membres = {}
        for username, nom, prenom in MEMBRES:
            user = User.objects.create_user(username, password=MOT_DE_PASSE_DEMO)
            membres[username] = Membre.objects.create(user=user, nom=nom, prenom=prenom, telephone="-",
                                                      email=f"{username}@projex.demo")

        projets = []
        for nom, description, equipe in PROJETS:
            projet = Projet.objects.create(nom=nom, description=description,
                                           date_debut=date(2026, 9, 1), date_fin=date(2027, 2, 26))
            projet.membres.set(membres[u] for u in equipe)
            projets.append(projet)

        for i_projet, auteur, type_, intitule, etat, remarque in TICKETS:
            ticket = Ticket.objects.create(projet=projets[i_projet], membre=membres[auteur], type=type_,
                                           Intitulé=intitule,
                                           description=f"<p>{intitule}. Ticket de démonstration.</p>")
            for etape in CHEMIN[etat]:
                ticket.changer_etat(etape, remarque=remarque if etape == "rejete" else None)

        premier = Ticket.objects.get(Intitulé__startswith="Pièce jointe")
        Comment.objects.create(ticket=premier, user=admin_user,
                               content="Reproduit avec un PDF de plus de 5 Mo, correction en cours.")
        Comment.objects.create(ticket=premier, user=membres["youssef"].user,
                               content="Merci, le fichier fait 7 Mo.")

        self.stdout.write(self.style.SUCCESS(
            f"Démo prête : admin / {MOT_DE_PASSE_DEMO} et membres salma, youssef, hind "
            f"(même mot de passe)."))
