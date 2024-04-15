# SCI-1402  - Projet final
Dépôt pour projet en science des données dans le cadre du cours SCI-1402
## Objectif
Ce projet a comme objectif la production d'une carte interactive présentant des prédictions des taux d’occupation aux urgences de différentes installations de santé sur le territoire du Québec.
## Source des données
Les données utilisées dans le modèle sont le [Fichier horaire des données de la situation à l’urgence](https://www.donneesquebec.ca/recherche/dataset/fichier-horaire-des-donnees-de-la-situation-a-l-urgence) et les [Fichiers cartographiques M02 des installations et établissements](https://www.donneesquebec.ca/recherche/dataset/fichiers-cartographiques-m02-des-installations-et-etablissements) provenant du site de [Données Québec](https://donneesquebec.ca),
##  Fonctionnement
Les données sont récoltées de façon horaire et stockées dans une base de données MongoDB sur la plateforme Atlas. Un modèle LSTM combiné utilisant la librairie keras est entraîné à l’aide de ces données. Des prédictions des taux d’occupation sont faites par ce modèle puis une carte des installations affichant ces prédictions est produite en utilisant la librairie pyplot.graph_objects.
## Composantes
### Répertoire **carte**
Ce répertoire contient le résultat du projet, soit la carte affichant des prédictions. Notons que GitHub n’affiche pas de prévision du fichier et qu’il doit être téléchargé pour être consulté.


