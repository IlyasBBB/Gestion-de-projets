# Design : tableau d'atelier

L'interface reprend les tableaux de management visuel des ateliers (obeya) : des colonnes d'état, des fiches cartonnées tenues par un aimant, un voyant andon qui s'allume quand quelque chose attend. Tout est dans `etc/assets/css/projex.css`.

## Couleurs

| Rôle | Variable | Valeur |
| --- | --- | --- |
| Fond (tôle émaillée) | `--tole` | `#e9e7e1` |
| Barre et texte (ardoise) | `--ardoise` | `#1e2a33` |
| Fiches | `--fiche` | `#fbfaf6` |
| Texte secondaire | `--encre-2` | `#4f5b64` |
| Anomalie | `--anomalie` | `#d94a2b` |
| Paramétrage, focus, action principale | `--parametrage` | `#f2b705` |
| Demande d'information, clôture | `--info` | `#3b7d5c` |

La couleur d'un type de ticket n'apparaît que sur l'aimant de sa fiche et sur la puce de la légende. Le jaune signal est réservé à l'action principale, à l'onglet courant et au focus clavier.

## Typographie

Barlow (Google Fonts), graisses 400, 600 et 800. Titres de colonnes et de panneaux en capitales espacées (0,1 em). Chiffres tabulaires partout (`font-variant-numeric: tabular-nums`).

## Composants

- Fiche : fond `--fiche`, rayon 6 px, ombre courte, aimant de 16 px en haut à droite ; elle se soulève au survol.
- Colonne : titre en capitales sur un trait de 3 px, compteur en 28 px.
- Badge d'état : pastille arrondie, teinte propre à chaque état.
- Boutons : ardoise par défaut, jaune pour l'action principale, rouge pour le rejet, vert pour la clôture, contour pour les actions secondaires.

## Mouvement

- Glisser une fiche (administrateur) : les colonnes autorisées par le workflow s'éclairent, les autres s'estompent. Au dépôt, la fiche se pose dans sa nouvelle colonne (View Transitions API quand le navigateur la connaît).
- Le voyant andon pulse tant que des tickets sont à l'état Déclaré.
- Page de connexion : un petit tableau en perspective où une fiche passe de colonne en colonne.
- `prefers-reduced-motion` coupe toutes les animations.

## Responsive

Sous 1100 px, le tableau défile horizontalement colonne par colonne. Sous 760 px, la navigation passe sur une deuxième ligne, les colonnes Projet et Type de la liste disparaissent et les tableaux larges défilent dans leur cadre.
