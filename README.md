# SCI-1402  - Projet final
Dépôt pour projet en science des données dans le cadre du cours SCI-1402
## Objectif
Ce projet a comme objectif la production d'une carte interactive présentant des prédictions des taux d’occupation aux urgences de différentes installations de santé sur le territoire du Québec.
## Source des données
Les données utilisées dans le modèle sont le [Fichier horaire des données de la situation à l’urgence](https://www.donneesquebec.ca/recherche/dataset/fichier-horaire-des-donnees-de-la-situation-a-l-urgence) et les [Fichiers cartographiques M02 des installations et établissements](https://www.donneesquebec.ca/recherche/dataset/fichiers-cartographiques-m02-des-installations-et-etablissements) provenant du site de [Données Québec](https://donneesquebec.ca),
##  Fonctionnement
Les données sont récoltées de façon horaire et stockées dans une base de données MongoDB sur la plateforme Atlas. Un modèle LSTM combiné utilisant la librairie keras est entraîné à l’aide de ces données. Des prédictions des taux d’occupation sont faites par ce modèle puis une carte des installations affichant ces prédictions est produite en utilisant la librairie pyplot.graph_objects.
## Composantes
### Répertoire carte
Le répertoire **carte** contient le résultat du projet, soit la [carte interactive des projections de taux d’occupation aux urgences](https://github.com/dekingsey/sci1402/blob/main/carte/carte_quebec.html), soit la carte affichant des prédictions. Notons que GitHub n’affiche pas ce fichier directement dans la plateforme en raison de sa taille et qu’il doit être téléchargé pour être consulté.
### Répertoire data
Le répertoire **data** contient des fichiers csv téléchargés de façon horaire. Ces fichiers peuvent être utilisés pour construire la base de données initiale. Ce répertoire est gardé à jour par une tâche planifiée.
### Répertoire modele

Le répertoire **modele** contient, dans le fichier modele.keras, une sauvegarde du modèle combiné LSTM utilisé pour produire les prédicitons et, dans le fichier modele.echelle, les échelles qui doivent être utilisées pour transformer les données produites par le modèle en données qui pourront être utilisées.
### Répertoire script
Le répertoire **script** contient un script bash **get_urgences** qui est utilisé sur un serveur pour collecter les fichiers csv contenus dans le répertoire **data**. Ce script est aussi en charge de mettre à jour les données du répertoire **data** et du répertoire **carte** sur GitHub. Il ne devrait être utilisé que sur notre serveur principal et n’est fourni ici qu’en guise de référence.
### Fichier python
- 
## Éléments requis
Une base de données MongoDB. La variable environnementale `MONGO_URI` doit contenir la chaîne de connexion pour cette base de données. 
### Librairies requises
Les libraires suivantes sont requises pour ce projet :
- pymongo
- keras
- pickle
- pandas
- plotly


