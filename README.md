# SCI-1402  - Projet en science des données
Dépôt pour projet en science des données dans le cadre du cours SCI-1402

## Objectif
Ce projet a comme objectif la production d'une carte interactive présentant des prédictions des taux d’occupation aux urgences de différentes installations de santé sur le territoire du Québec.

## Fonctionnement
Pour plus de détails sur le fonctionnement et l'utilisation du projet, consultez [FONCTIONNEMENT.md](/FONCTIONNEMENT.md).

## Résultat
La [carte interactive des projections de taux d’occupation aux urgences](https://github.com/dekingsey/sci1402/blob/main/carte/carte_quebec.html) produite par ce projet est disponible directement à partir de ce dépôt GitHub et est mise à jour en temps réel de façon horaire.

## Source des données
Les données brutes utilisées dans le modèle sont le [Fichier horaire des données de la situation à l’urgence](https://www.donneesquebec.ca/recherche/dataset/fichier-horaire-des-donnees-de-la-situation-a-l-urgence) et les [Fichiers cartographiques M02 des installations et établissements](https://www.donneesquebec.ca/recherche/dataset/fichiers-cartographiques-m02-des-installations-et-etablissements) provenant du site de [Données Québec](https://donneesquebec.ca), à partir du 8 février 2024.

## Contenu du dépôt
### Répertoire carte
Le répertoire `carte` contient le résultat du projet, soit la [carte interactive des projections de taux d’occupation aux urgences](https://github.com/dekingsey/sci1402/blob/main/carte/carte_quebec.html), affichant les prédictions. Notons que GitHub n’affiche pas ce fichier directement dans la plateforme en raison de sa taille et qu’il doit être téléchargé pour être consulté.

### Répertoire data
Le répertoire `data` contient des fichiers csv téléchargés de façon horaire. Ces fichiers peuvent être utilisés pour construire la base de données initiale ou mettre à jour une base de données après une période d'inactivité. Ce répertoire est gardé à jour par une tâche planifiée.

### Répertoire modele
Le répertoire `modele` contient, dans le fichier modele.keras, une sauvegarde du modèle combiné LSTM utilisé pour produire les prédicitons et, dans le fichier modele.echelle, les échelles qui doivent être utilisées pour transformer les données produites par le modèle en données qui pourront être utilisées.

### Répertoire script
Le répertoire `script` contient un script bash `get_urgences` qui est utilisé sur un serveur pour collecter les fichiers csv contenus dans le répertoire `data`. Ce script est aussi en charge de mettre à jour les données du répertoire `data` et du répertoire `carte` sur GitHub. Notons que les scripts de ce répertoire ne devraient être utilisé que sur notre serveur principal et ne sont fournis ici qu’en guise de référence.

### Fichiers python
Les fichiers .py dans la racine du projet représentent le cœur du projet. Le fichier `urgences_menu.py` peut être lancé pour exécuter les différentes tâches d’initialisation et de fonctionnement en continu du projet.

## Éléments requis
Une base de données MongoDB. La variable environnementale `MONGO_URI` doit contenir la chaîne de connexion pour cette base de données. 
### Librairies requises
Les libraires suivantes sont requises pour ce projet :
- `pymongo`
- `keras`
- `pickle`
- `pandas`
- `plotly`
