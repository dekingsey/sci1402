# SCI-1402  - Projet final
Dépôt pour projet en science des données dans le cadre du cours SCI-1402

## Objectif
Ce projet a comme objectif la production d'une carte interactive présentant des prédictions des taux d’occupation aux urgences de différentes installations de santé sur le territoire du Québec.

###  Fonctionnement
Les données sont récoltées de façon horaire à partir du site de Données Québec, épurées et stockées dans une base de données MongoDB sur la plateforme Atlas.

Un modèle  combiné utilisant la librairie keras est entraîné à l’aide de ces données. Le modèle choisi est un réseau de neurones LSTM profond dont le résultat est combiné à des données non-temporelles pour être traité par trois couches de neurones Dense produisant un prédiction des taux d'occupation:
![Réseau de neurones](/ressources/RNA.png)<BR/>

La performance du modèle a été mesurée en calculant l'erreur quadratique moyenne (MSE) entre la prédiction et la valeur réelle. L'objectif à atteindre avec le modèle était une performance supérieure à l'utilisation de la dernière donnée précédent la donnée à prédire. 
```
Cible à battre: 0.00213267531385084
Score: 0.0020986351166595576
```

Suite à l'acquisition de nouvelles données ou lorsque les prédictions ne sont valides que pour 15 minutes ou moins, des prédicitons sont faites en utilisant ce modèle et stockée dans la base de données. Par la suite une carte des installations affichant ces prédictions est produite en utilisant la librairie pyplot.graph_objects:
![Réseau de neurones](/ressources/RNA.png)<BR/>

### Résultat
La [carte interactive des projections de taux d’occupation aux urgences](https://github.com/dekingsey/sci1402/blob/main/carte/carte_quebec.html) produite par ce projet est disponible dans ce répertoire GitHub et mise à jour en temps réel de façon horaire.

### Source des données
Les données utilisées dans le modèle sont le [Fichier horaire des données de la situation à l’urgence](https://www.donneesquebec.ca/recherche/dataset/fichier-horaire-des-donnees-de-la-situation-a-l-urgence) et les [Fichiers cartographiques M02 des installations et établissements](https://www.donneesquebec.ca/recherche/dataset/fichiers-cartographiques-m02-des-installations-et-etablissements) provenant du site de [Données Québec](https://donneesquebec.ca),

## Composantes
### Répertoire carte
Le répertoire `carte` contient le résultat du projet, soit la [carte interactive des projections de taux d’occupation aux urgences](https://github.com/dekingsey/sci1402/blob/main/carte/carte_quebec.html), soit la carte affichant des prédictions. Notons que GitHub n’affiche pas ce fichier directement dans la plateforme en raison de sa taille et qu’il doit être téléchargé pour être consulté.

### Répertoire data
Le répertoire `data` contient des fichiers csv téléchargés de façon horaire. Ces fichiers peuvent être utilisés pour construire la base de données initiale. Ce répertoire est gardé à jour par une tâche planifiée.
### Répertoire modele

### Répertoire modele
Le répertoire `modele` contient, dans le fichier modele.keras, une sauvegarde du modèle combiné LSTM utilisé pour produire les prédicitons et, dans le fichier modele.echelle, les échelles qui doivent être utilisées pour transformer les données produites par le modèle en données qui pourront être utilisées.

### Répertoire script
Le répertoire `script` contient un script bash `get_urgences` qui est utilisé sur un serveur pour collecter les fichiers csv contenus dans le répertoire `data`. Ce script est aussi en charge de mettre à jour les données du répertoire `data` et du répertoire `carte` sur GitHub. Il ne devrait être utilisé que sur notre serveur principal et n’est fourni ici qu’en guise de référence.

### Fichiers python
Les fichiers .py dans la racine du projet représentent le cœur du projet. Le fichier `urgences_menu.py` peut être lancé pour exécuter les différentes tâches d’initialisation et de fonctionnement en continu du projet.

## Éléments requis
Une base de données MongoDB. La variable environnementale `MONGO_URI` doit contenir la chaîne de connexion pour cette base de données. 
### Librairies requises
Les libraires suivantes sont requises pour ce projet :
- pymongo
- keras
- pickle
- pandas
- plotly


