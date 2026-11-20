# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Équipe d'origine** : l'équipe de la Digital Factory de Cosumar (6 personnes), qui a utilisé l'application pour déclarer, répartir et suivre les tickets de ses projets internes. Développée par Ilyas Ben Alla pendant son stage de juillet-août 2024.
- **Public prioritaire de cette version** : un recruteur ou un ingénieur qui ouvre la démo et doit comprendre en deux minutes le workflow, les rôles et le tableau de bord, avec des comptes de démonstration (admin et membre) et des données fictives.

## Product Purpose

Centraliser les demandes adressées à une équipe SI (anomalies, paramétrages système, demandes d'information), les rattacher à un projet, les faire avancer dans un workflow contrôlé et donner aux administrateurs une vue chiffrée de l'avancement. Réussite : chaque ticket a un état clair, un responsable et un historique, et l'admin voit où en est chaque projet.

## Positioning

Outil interne de support SI conçu à partir des besoins réels d'une équipe (cahier des charges clarifié par prototypes successifs avec les utilisateurs), pas un clone générique de Jira : vocabulaire métier français, trois types de demande, workflow à 5 états appliqué côté serveur.

## Operating Context

- Deux rôles : **administrateur** (crée membres et projets, fait avancer les tickets, voit les statistiques) et **membre** (déclare des tickets sur ses projets, suit les siens, commente).
- Workflow : déclaré → en cours d'analyse → en cours de traitement → clôturé ; rejet possible après analyse, obligatoirement motivé par une remarque.
- Notifications internes à chaque création ou changement d'état. Commentaires par ticket. Filtres par projet et statut, tri par date ou ordre alphabétique, pagination.

## Capabilities and Constraints

- Django 5.2, SQLite, templates serveur, TinyMCE pour la description des tickets. Pas de SPA : l'interface reste des templates Django avec du JS progressif.
- Tableau de bord alimenté par trois endpoints JSON : tickets par état, répartition par type, taux de clôture par projet.
- Nom de l'application : **ProjeX**. Pas de logo ni de marque Cosumar dans l'interface ou la démo publique (le code peut appartenir à Cosumar ; pas de licence open source).

## Brand Commitments

- Nom : ProjeX. Langue de l'interface : français.
- Aucune marque tierce dans l'interface.

## Evidence on Hand

- Code et workflow réels du dépôt. Données de démonstration : fictives et présentées comme telles.
- À ne pas inventer : nombre de tickets traités, gains de temps, chiffres d'adoption, témoignages.

## Product Principles

1. L'état d'un ticket et la prochaine action possible se lisent en un coup d'œil.
2. Chaque rôle ne voit que ce qui le concerne ; les règles sont appliquées par le serveur, pas seulement masquées dans l'interface.
3. Tout ce que montre la démo existe vraiment dans le code.
4. La démo se comprend sans mode d'emploi.
